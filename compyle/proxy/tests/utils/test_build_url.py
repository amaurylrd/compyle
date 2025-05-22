# pylint: disable=missing-function-docstring

from django.test import SimpleTestCase

from compyle.proxy import utils


class TestBuildUrl(SimpleTestCase):
    """TestCase for the `build_url` method in the utils module."""

    def test_basic_url_and_slug(self) -> None:
        base_url = "https://example.com"
        slug = "/api/v1"
        result = utils.build_url(base_url, slug)

        self.assertEqual(result, "https://example.com/api/v1")

    def test_slug_without_leading_slash(self) -> None:
        base_url = "https://example.com"
        slug = "api/v1"
        result = utils.build_url(base_url, slug)

        self.assertEqual(result, "https://example.com/api/v1")

    def test_url_with_existing_path(self) -> None:
        base_url = "https://example.com/base"
        slug = "/api"
        result = utils.build_url(base_url, slug)

        self.assertEqual(result, "https://example.com/base/api")

    def test_base_url_with_trailing_slash(self) -> None:
        base_url = "https://example.com/"
        slug = "api/v1"
        result = utils.build_url(base_url, slug)

        self.assertEqual(result, "https://example.com/api/v1")

    def test_with_query_params(self) -> None:
        base_url = "https://example.com"
        slug = "/api"
        result = utils.build_url(base_url, slug, foo="bar", q="test")

        self.assertIn(
            result,
            ["https://example.com/api?foo=bar&q=test", "https://example.com/api?q=test&foo=bar"],
        )

    def test_no_params(self) -> None:
        base_url = "https://example.com"
        slug = "/api"
        result = utils.build_url(base_url, slug)

        self.assertEqual(result, "https://example.com/api")

    def test_empty_slug(self) -> None:
        base_url = "https://example.com"
        slug = ""
        result = utils.build_url(base_url, slug)

        self.assertEqual(result, base_url)

    def test_existing_query_replaced(self) -> None:
        base_url = "https://example.com?old=val"
        slug = "/new"
        result = utils.build_url(base_url, slug, new="val")

        self.assertEqual(result, "https://example.com/new?new=val")

    def test_remove_fragment(self) -> None:
        base_url = "https://example.com/path#fragment"
        slug = "/more"
        result = utils.build_url(base_url, slug)

        self.assertEqual(result, "https://example.com/path/more#fragment")
