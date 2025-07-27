import uuid
from typing import Optional


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


def generate_id(prefix: Optional[str] = None) -> str:
    """Generate a unique order ID using UUID.

    Args:
        prefix: Optional prefix to add to the order ID.

    Returns:
        Unique order ID string.

    Examples:
        >>> generate_id()
        'f47ac10b-58cc-4372-a567-0e02b2c3d479'

        >>> generate_id(prefix="ORDER")
        'ORDER_f47ac10b-58cc-4372-a567-0e02b2c3d479'

        >>> generate_id(prefix="SHOP")
        'SHOP_f47ac10b-58cc-4372-a567-0e02b2c3d479'
    """
    unique_id = str(uuid.uuid4())

    if prefix:
        return f"{prefix}_{unique_id}"

    return unique_id


def generate_short_id(prefix: Optional[str] = None, length: int = 8) -> str:
    """Generate a shorter unique order ID using UUID.

    Args:
        prefix: Optional prefix to add to the order ID.
        length: Length of the UUID portion (default: 8 characters).

    Returns:
        Shorter unique order ID string.

    Examples:
        >>> generate_short_id()
        'f47ac10b'

        >>> generate_short_id(prefix="ORD", length=12)
        'ORD_f47ac10b58cc'
    """
    unique_id = str(uuid.uuid4()).replace("-", "")[:length]

    if prefix:
        return f"{prefix}_{unique_id}"

    return unique_id
