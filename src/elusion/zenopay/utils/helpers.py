def format_amount(amount: int, currency: str = "TZS") -> str:
    """Format payment amount for display.

    Args:
        amount: Amount in smallest currency unit.
        currency: Currency code.

    Returns:
        Formatted amount string.
    """
    if currency == "TZS":
        return f"{amount:,} {currency}"
    else:
        amount_decimal = amount / 100
        return f"{amount_decimal:.2f} {currency}"


def parse_amount(amount_str: str, currency: str = "TZS") -> int:
    """Parse amount string to integer in smallest currency unit.

    Args:
        amount_str: Amount string to parse.
        currency: Currency code.

    Returns:
        Amount as integer in smallest currency unit.
    """
    try:
        amount_float = float(amount_str.replace(",", ""))
        if currency == "TZS":
            return int(amount_float)
        else:
            return int(amount_float * 100)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid amount format: {amount_str}")
