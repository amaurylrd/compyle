# pylint: disable=missing-function-docstring

import unittest

from compyle.proxy import utils


class TestExtractParams(unittest.TestCase):
    """TestCase for the `extract_url_params` method in the utils module."""

    def test_no_params(self):
        url = "https://example.com/path"

        self.assertEqual(utils.extract_url_params(url), [])

    def test_single_param(self):
        url = "https://example.com/path?foo=bar"

        self.assertEqual(utils.extract_url_params(url), [("foo", "bar")])

    def test_multiple_params(self):
        url = "https://example.com/path?a=1&b=2&c=3"

        self.assertEqual(utils.extract_url_params(url), [("a", "1"), ("b", "2"), ("c", "3")])

    def test_blank_value(self):
        url = "https://example.com/path?foo="

        self.assertEqual(utils.extract_url_params(url), [("foo", "")])

    def test_duplicate_keys(self):
        url = "https://example.com/path?x=1&x=2"

        self.assertEqual(utils.extract_url_params(url), [("x", "1"), ("x", "2")])

    def test_param_with_special_chars(self):
        url = "https://example.com/path?q=hello%20world&sort=name%26desc"

        self.assertEqual(utils.extract_url_params(url), [("q", "hello world"), ("sort", "name&desc")])

    def test_with_fragment(self):
        url = "https://example.com/path?a=1#section"

        self.assertEqual(utils.extract_url_params(url), [("a", "1")])
