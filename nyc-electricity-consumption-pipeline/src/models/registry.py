"""Model name -> estimator for the regression suite compared in train.py."""

from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from xgboost import XGBRegressor

MODEL_REGISTRY = {
    "linear_regression": LinearRegression(),
    "ridge": Ridge(alpha=1.0, random_state=42),
    "random_forest": RandomForestRegressor(n_estimators=300, max_depth=12, n_jobs=-1, random_state=42),
    "gradient_boosting": GradientBoostingRegressor(n_estimators=300, max_depth=3, learning_rate=0.05, random_state=42),
    "xgboost": XGBRegressor(n_estimators=400, max_depth=5, learning_rate=0.05, n_jobs=-1, random_state=42),
}
