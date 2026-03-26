USD_MULTIPLIER = 1.065


def to_usd_display(amount: float | int) -> float:
    return float(amount) * USD_MULTIPLIER


def from_usd_input(amount: float | int) -> float:
    return float(amount) / USD_MULTIPLIER


def format_usd(amount: float | int, decimals: int = 0) -> str:
    displayed = to_usd_display(amount)
    if decimals <= 0:
        return f"${displayed:,.0f}"
    return f"${displayed:,.{decimals}f}"


def usd_to_internal_from_text(amount: float | int) -> int:
    return int(round(from_usd_input(amount)))
