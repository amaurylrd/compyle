# pylint: disable=missing-function-docstring

import unittest

from compyle.proxy import utils


class TestNormalizeUrl(unittest.TestCase):
    """TestCase for the `normalize_url` method in the utils module."""

    def test_add_trailing_slash_when_missing(self) -> None:
        url = "https://example.com/api"
        result = utils.normalize_url(url, True)

        self.assertEqual(result, "https://example.com/api/")

    def test_no_change_if_already_has_slash_and_wants_slash(self) -> None:
        url = "https://example.com/api/"
        result = utils.normalize_url(url, True)

        self.assertEqual(result, "https://example.com/api/")

    def test_remove_trailing_slash_when_not_wanted(self) -> None:
        url = "https://example.com/api/"
        result = utils.normalize_url(url, False)

        self.assertEqual(result, "https://example.com/api")

    def test_no_change_if_already_no_slash_and_does_not_want_slash(self) -> None:
        url = "https://example.com/api"
        result = utils.normalize_url(url, False)

        self.assertEqual(result, "https://example.com/api")

    def test_double_slash_handling_is_preserved(self) -> None:
        url = "https://example.com/api//"
        result = utils.normalize_url(url, False)

        self.assertEqual(result, "https://example.com/api")

    def test_query_string_preserved(self) -> None:
        url = "https://example.com/api?foo=bar"
        result = utils.normalize_url(url, True)

        self.assertEqual(result, "https://example.com/api/?foo=bar")
