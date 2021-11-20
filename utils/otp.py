from random import choices
from string import ascii_letters, digits


def generate_code(length=6) -> str:
    """
    Generate a numeric code.
    """
    return ''.join(choices(digits, k=length))


def generate_alphanumeric_code(length=6) -> str:
    """
    Generates an alpha-numeric code.
    """
    return ''.join(choices(ascii_letters + digits, k=length))
