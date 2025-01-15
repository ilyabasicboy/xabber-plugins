from django.core.exceptions import ValidationError
import re


def validate_slug(value):
    # Regular expression for validating a slug
    if not re.match(r'^[a-zA-Z0-9_-]+$', value):
        raise ValidationError(
            '%(value)s is not a valid slug. Only letters, numbers, hyphens, and underscores are allowed.',
            params={'value': value},
        )