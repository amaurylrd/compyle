from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class ReferenceValidator(RegexValidator):
    """Validates the reference field for the BaseModel model."""

    def __init__(self) -> None:
        super().__init__(
            regex=r"^[0-9a-zA-Z_-]*$",
            message=_("Only alphanumeric characters, underscores or hyphens are allowed."),
        )
