import math
import time

from config.settings import resolve_force_strategy

def calculate_metrics(profile: dict) -> dict:
    """
    Calculates the Sustainability Index (S_i) and Confidence Score (C_s)
    based on the user's financial profile.

    This function utilizes the Gaussian Penalty Function for S_i and a weighted 
    time-decay function for C_s.

    Parameters:
    - profile (dict): A dictionary containing 'mu_hist', 'sigma_hist', 'beta_prop', 
                      'last_update_timestamp', 'data_completeness', and 'market_volatility'.

    Returns:
    - dict: A dictionary with the keys "s_i" (float) and "c_s" (float).
    """

    # 1. Sustainability Index (S_i) Logic (Gaussian Penalty Function)
    mu_hist = profile.get("mu_hist", 0.0)
    sigma_hist = profile.get("sigma_hist", 0.0)
    beta_prop = profile.get("beta_prop", 0.0)

    # Note: If sigma_hist is 0, default S_i to 1.0 if beta_prop <= mu_hist, else 0.5.
    if sigma_hist == 0:
        s_i = 1.0 if beta_prop <= mu_hist else 0.5
    else:
        # Formula: S_i = e^(-(beta_prop - mu_hist)^2 / 2*(sigma_hist^2))
        exponent = -((beta_prop - mu_hist) ** 2) / (2 * (sigma_hist ** 2))
        s_i = math.exp(exponent)

    # 2. Confidence Score (C_s) Logic
    last_update_timestamp = profile.get("last_update_timestamp", time.time())
    r_comp = profile.get("data_completeness", 1.0)
    v_mkt = profile.get("market_volatility", 0.0)

    current_time = time.time()
    
    # Calculate Δt in days (assuming timestamps are in seconds)
    delta_t_seconds = max(0, current_time - last_update_timestamp)
    delta_t_days = delta_t_seconds / (24 * 3600)
    
    # Weight 1 (Freshness): use decay function f(Δt) = e^(-0.1 * Δt)
    f_delta_t = math.exp(-0.1 * delta_t_days)
    
    # Formula: C_s = (0.5 * f(Δt)) + (0.3 * R_comp) + (0.2 * V_mkt)
    c_s = (0.5 * f_delta_t) + (0.3 * r_comp) + (0.2 * v_mkt)

    return {
        "s_i": float(s_i),
        "c_s": float(c_s)
    }

def determine_strategy(s_i: float) -> str:
    """
    Determines the strategy to trigger based on the Decision Tree logic constraints:
    - If S_i < 0.5 -> Strategy B (Goal Re-alignment)
    - If 0.5 <= S_i < 0.8 -> Strategy A (Cost Optimization)
    - If S_i >= 0.8 -> None (Sustainable)
    """
    if s_i < 0.5:
        return "B"
    elif s_i < 0.8:
        return "A"
    else:
        return "None"


def build_profile_from_user_context(user_context: dict) -> dict:
    monthly_spending = float(user_context.get("monthly_spending", 0.0) or 0.0)
    return {
        "mu_hist": monthly_spending * 0.9,
        "sigma_hist": monthly_spending * 0.15,
        "beta_prop": monthly_spending,
        "last_update_timestamp": time.time() - 86400,
        "data_completeness": 0.85,
        "market_volatility": 0.3,
    }


def evaluate_user_context(user_context: dict) -> dict:
    profile = build_profile_from_user_context(user_context)
    metrics = calculate_metrics(profile)
    strategy = resolve_force_strategy() or determine_strategy(metrics["s_i"])
    return {
        **metrics,
        "strategy": strategy,
    }


def map_strategy_to_goal_status(strategy: str, progress_percent: int | None = None) -> str:
    if progress_percent is not None and progress_percent >= 100:
        return "completed"
    return "at_risk" if strategy in {"A", "B"} else "on_track"
