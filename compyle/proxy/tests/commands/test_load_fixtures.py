from unittest import mock

from django.core.management import call_command
from django.test import SimpleTestCase


class LoadFixturesCommandTest(SimpleTestCase):
    """TestCase for the `load_fixtures` command in the commands module."""

    @mock.patch("django.core.management.call_command")
    def test_load_fixtures_command_calls_loaddata_for_each_fixture(self, mock_call_command: mock.MagicMock) -> None:
        call_command("load_fixtures")

        expected_calls = [("loaddata", "twitch.json"), ("loaddata", "youtube.json")]
        actual_calls = [call.args for call in mock_call_command.call_args_list]

        self.assertEqual(actual_calls, expected_calls)
        self.assertEqual(mock_call_command.call_count, len(expected_calls))
