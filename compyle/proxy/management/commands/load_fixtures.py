from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _


# pylint: disable=missing-class-docstring
class Command(BaseCommand):
    help = _("Load demo fixture data")

    # pylint: disable=unused-argument, no-self-use
    def handle(self, *args, **options) -> None:
        """Handle the command `load_fixtures`."""
        call_command("loaddata", "twitch.json")
        call_command("loaddata", "youtube.json")
