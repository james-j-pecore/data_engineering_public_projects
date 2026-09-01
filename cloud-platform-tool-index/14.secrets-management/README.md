# Secrets Management

## Overview

Services for securely storing and retrieving credentials, API keys, connection strings, and other sensitive configuration — used by pipeline jobs and applications to avoid hardcoding secrets in code or config files.

---

## Comparison table

| | AWS | GCP | Azure |
|---|---|---|---|
| Primary secrets service | Secrets Manager | Secret Manager | Key Vault |
| Cheaper/simpler alternative on same cloud | Systems Manager Parameter Store | — (Secret Manager is the only option) | — (Key Vault covers all tiers) |
| Cryptographic key management | KMS (separate service) | Cloud KMS (separate service) | Key Vault (same service) |
| Certificate management | ACM (separate service) | Certificate Manager (separate service) | Key Vault (same service) |
| Built-in automatic rotation | Yes (Secrets Manager) | No (self-wired via Cloud Functions/Scheduler) | Yes |

---

## What it's for

- **Database and API credentials** — connection strings, passwords, tokens that pipeline jobs need at runtime without being embedded in code.
- **Rotation-sensitive secrets** — credentials that need periodic automatic rotation (e.g., database passwords) without redeploying dependent services.
- **Cryptographic keys and certificates** — encryption keys and TLS certificates, which some providers manage in the same service as secrets and others split out.

---

## Key differences

**AWS splits secrets storage across two services with overlapping purposes**, creating a "which one do I use" decision that GCP and Azure don't have. **Secrets Manager** is the fuller-featured, paid option with built-in automatic rotation (especially well-integrated for RDS database credentials) and fine-grained resource policies. **Parameter Store** (part of Systems Manager) offers a free tier for basic key-value config/secret storage without the rotation automation — commonly used for simpler configuration values where rotation isn't needed, purely to avoid Secrets Manager's per-secret cost. Many AWS shops end up using both: Parameter Store for general config, Secrets Manager specifically for credentials needing rotation.

**Azure Key Vault uniquely bundles three categories into one service**: secrets, cryptographic keys (including HSM-backed keys), and TLS certificates. AWS and GCP both split these across separate, purpose-built services — AWS uses Secrets Manager (secrets), KMS (keys), and ACM (certificates); GCP uses Secret Manager (secrets), Cloud KMS (keys), and Certificate Manager (certificates). Key Vault's consolidation means one access-control and auditing model covers all three categories on Azure, versus coordinating policies across two or three separate services on AWS/GCP.

**GCP Secret Manager is the most narrowly scoped and simplest of the three** — purely a secrets store, with no built-in automatic rotation mechanism. Rotation on GCP is typically self-implemented by wiring up a Cloud Function on a Cloud Scheduler trigger to rotate the secret and update its value — more setup work than Secrets Manager's or Key Vault's built-in rotation policies, but a simpler mental model with fewer built-in moving parts.

---

## When to reach for it vs. alternatives

- On AWS, default to Parameter Store for non-sensitive or non-rotating configuration to avoid unnecessary Secrets Manager cost, and reserve Secrets Manager for credentials that need automatic rotation or fine-grained resource policies.
- On Azure, Key Vault is the single answer for secrets, keys, and certificates — no need to evaluate alternatives within Azure itself.
- On GCP, budget extra setup time for rotation logic if the secret needs to rotate automatically, since Secret Manager doesn't provide it out of the box.
- Regardless of provider, never store secrets in plain environment variables or config files checked into version control — inject them at runtime from the managed secrets service.

---

## Resources

- [AWS Secrets Manager documentation](https://docs.aws.amazon.com/secretsmanager/) · [Parameter Store documentation](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html)
- [GCP Secret Manager documentation](https://cloud.google.com/secret-manager/docs)
- [Azure Key Vault documentation](https://learn.microsoft.com/en-us/azure/key-vault/)
