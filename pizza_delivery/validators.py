import re

from django import forms


def customer_name_validator(name: str) -> str:
    if not name:
        raise forms.ValidationError("Name is required")
    if name[0].islower():
        raise forms.ValidationError("Name must start with uppercase letter")
    if len(name.strip()) < 2:
        raise forms.ValidationError("Name must be at least 2 letters long")
    if any(not char.isalpha() and char != " " for char in name):
        raise forms.ValidationError("Name must contain only letters or space")
    return name


def customer_phone_number_validator(phone_number: str) -> str:
    if not phone_number:
        raise forms.ValidationError("Phone number is required")
    return phone_number


def customer_address_validator(address: str) -> str:
    if not address:
        raise forms.ValidationError("Address is required")

    if len(address) < 10:
        raise forms.ValidationError(
            "Address must be at least 10 characters long"
        )

    if len(address) > 255:
        raise forms.ValidationError(
            "Address must be at most 255 characters long"
        )

    letters = [letter for letter in address if letter.isalpha()]
    if len(letters) < 8:
        raise forms.ValidationError("Address must contain at least 8 letters")

    digits = [digit for digit in address if digit.isdigit()]
    if len(digits) < 1:
        raise forms.ValidationError("Address must contain at least 1 digit")
    return address
