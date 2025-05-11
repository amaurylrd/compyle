# pylint: disable=missing-function-docstring

import unittest

from compyle.proxy import utils


class TestAddParams(unittest.TestCase):
    """TestCase for the `add_url_params` method in the utils module."""

    def test_add_single_param(self) -> None:
        url = "https://example.com/api"
        updated = utils.add_url_params(url, foo="bar")

        self.assertIn("foo=bar", updated)
        self.assertTrue(updated.startswith("https://example.com/api?"))

    def test_add_multiple_params(self) -> None:
        url = "https://example.com/api"
        updated = utils.add_url_params(url, a="1", b="2")

        self.assertIn("a=1", updated)
        self.assertIn("b=2", updated)

    def test_overwrite_existing_param(self) -> None:
        url = "https://example.com/api?foo=old"
        updated = utils.add_url_params(url, foo="new")

        self.assertIn("foo=new", updated)
        self.assertNotIn("foo=old", updated)

    def test_preserve_existing_params(self) -> None:
        url = "https://example.com/api?x=1"
        updated = utils.add_url_params(url, y="2")

        self.assertIn("x=1", updated)
        self.assertIn("y=2", updated)

    def test_add_param_with_blank_value(self) -> None:
        url = "https://example.com/api"
        updated = utils.add_url_params(url, empty="")

        self.assertIn("empty=", updated)

    def test_add_to_url_with_fragment(self) -> None:
        url = "https://example.com/api#section"
        updated = utils.add_url_params(url, q="1")

        self.assertIn("q=1", updated)
        self.assertTrue(updated.endswith("#section"))
