"""Minimal Spotify Web API client: Authorization Code OAuth + paginated, rate-limited GET."""

import json
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode, urlparse, parse_qs

import requests

from src import config

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE = "https://api.spotify.com/v1"


class _CallbackHandler(BaseHTTPRequestHandler):
    """One-shot HTTP handler that captures the `code` query param from the OAuth redirect."""

    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        self.server.auth_code = query.get("code", [None])[0]
        self.server.auth_error = query.get("error", [None])[0]

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        message = "You can close this tab and return to the terminal." if self.server.auth_code else "Authorization failed. Check the terminal."
        self.wfile.write(f"<html><body><p>{message}</p></body></html>".encode())

    def log_message(self, *args):
        pass  # silence default request logging


def _capture_auth_code(redirect_uri: str) -> str:
    parsed = urlparse(redirect_uri)
    server = HTTPServer((parsed.hostname, parsed.port), _CallbackHandler)
    server.auth_code = None
    server.auth_error = None
    server.handle_request()  # blocks for exactly one request

    if server.auth_error or not server.auth_code:
        raise RuntimeError(f"Spotify authorization failed: {server.auth_error}")
    return server.auth_code


def _load_cached_token() -> dict | None:
    if config.TOKEN_CACHE_PATH.exists():
        return json.loads(config.TOKEN_CACHE_PATH.read_text())
    return None


def _save_token(token: dict) -> None:
    token["expires_at"] = time.time() + token["expires_in"]
    config.TOKEN_CACHE_PATH.write_text(json.dumps(token))


def _request_token(payload: dict) -> dict:
    response = requests.post(
        TOKEN_URL,
        data=payload,
        auth=(config.SPOTIFY_CLIENT_ID, config.SPOTIFY_CLIENT_SECRET),
    )
    response.raise_for_status()
    token = response.json()
    _save_token(token)
    return token


def _run_authorization_code_flow() -> dict:
    params = {
        "client_id": config.SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": config.SPOTIFY_REDIRECT_URI,
        "scope": " ".join(config.SPOTIFY_SCOPES),
    }
    webbrowser.open(f"{AUTH_URL}?{urlencode(params)}")
    print("Opened browser for Spotify login. Waiting for redirect...")

    auth_code = _capture_auth_code(config.SPOTIFY_REDIRECT_URI)
    return _request_token(
        {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": config.SPOTIFY_REDIRECT_URI,
        }
    )


def _refresh_token(refresh_token: str) -> dict:
    token = _request_token({"grant_type": "refresh_token", "refresh_token": refresh_token})
    # Spotify doesn't always return a new refresh_token; keep the old one if so.
    token.setdefault("refresh_token", refresh_token)
    _save_token(token)
    return token


def get_access_token() -> str:
    """Returns a valid access token, authenticating or refreshing as needed."""
    token = _load_cached_token()

    if token is None:
        token = _run_authorization_code_flow()
    elif time.time() >= token["expires_at"] - 60:
        token = _refresh_token(token["refresh_token"])

    return token["access_token"]


class SpotifyClient:
    """Thin wrapper around the Spotify Web API with pagination + rate-limit handling."""

    def __init__(self):
        self._session = requests.Session()

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {get_access_token()}"}

    def get(self, path: str, params: dict | None = None) -> dict:
        """GET a single Spotify API resource, retrying once on 429 rate limiting."""
        url = path if path.startswith("http") else f"{API_BASE}{path}"

        response = self._session.get(url, headers=self._headers(), params=params)
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 1))
            print(f"Rate limited, waiting {retry_after}s...")
            time.sleep(retry_after)
            response = self._session.get(url, headers=self._headers(), params=params)

        response.raise_for_status()
        return response.json()

    def get_paginated(self, path: str, params: dict | None = None) -> list[dict]:
        """Follows Spotify's `next` cursor to collect every page of a list endpoint."""
        items: list[dict] = []
        url, url_params = path, dict(params or {}, limit=50)

        while url:
            page = self.get(url, url_params)
            items.extend(page["items"])

            url, url_params = page.get("next"), None
            if url:
                time.sleep(0.1)  # small courtesy delay between pages

        return items
