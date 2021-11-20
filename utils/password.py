from string import digits
from typing import Union


def validate_password(password: str) -> Union[str, None]:
    """
    Validates a password.
    :param password: The password to validate.
    :return: None if the password is valid or return all error messages.
    """

    if len(password) < 8:
        return "Password must be at least 8 characters long."

    pwd_set = set(password)
    if len(pwd_set.intersection(digits)) == 0:
        return "Password must contain at least one digit."

    return None
