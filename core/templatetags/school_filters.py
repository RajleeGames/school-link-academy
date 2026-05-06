from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


def _to_decimal(value):
    if value is None or value == "":
        return Decimal("0")

    try:
        clean_value = str(value).replace(",", "").strip()
        return Decimal(clean_value)
    except (InvalidOperation, ValueError, TypeError):
        return Decimal("0")


@register.filter
def numcomma(value):
    """
    Format number with commas in every language.
    Example: 2800000 -> 2,800,000
    """
    number = _to_decimal(value)
    return f"{number:,.0f}"


@register.filter
def money0(value):
    """
    Format money number only.
    Example: 2800000 -> 2,800,000
    """
    number = _to_decimal(value)
    return f"{number:,.0f}"


@register.filter
def money2(value):
    """
    Format money with two decimal places.
    Example: 2800000 -> 2,800,000.00
    """
    number = _to_decimal(value)
    return f"{number:,.2f}"


@register.filter
def tzs(value):
    """
    Format Tanzania money.
    Example: 2800000 -> TZS 2,800,000
    """
    number = _to_decimal(value)
    return f"TZS {number:,.0f}"