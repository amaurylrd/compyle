# pylint: disable=missing-function-docstring

from unittest import mock

import requests
from django.test import TestCase

from compyle.proxy import choices


class TestHttpMethod(TestCase):
    """TestCase for the `HttpMethod` enum in the choices module."""

    def setUp(self) -> None:  # pylint: disable=invalid-name
        super().setUp()

        self.url = "https://localhost"

    def test_http_method_func(self):
        self.assertEqual(choices.HttpMethod.POST.func, requests.post)
        self.assertEqual(choices.HttpMethod.PUT.func, requests.put)
        self.assertEqual(choices.HttpMethod.PATCH.func, requests.patch)
        self.assertEqual(choices.HttpMethod.DELETE.func, requests.delete)

    @mock.patch("requests.api.request")
    def test_can_listener_http_verb_request_post(self, mock_request: mock.MagicMock) -> None:
        http_method = choices.HttpMethod.POST

        response = http_method(self.url)

        mock_request.assert_called_once_with(http_method.value, self.url, data=None, json=None)
        self.assertEqual(response, mock_request.return_value)

    @mock.patch("requests.api.request")
    def test_can_listener_http_verb_request_patch(self, mock_request: mock.MagicMock) -> None:
        http_method = choices.HttpMethod.PATCH
        response = http_method(self.url)

        mock_request.assert_called_once_with(http_method.value, self.url, data=None)
        self.assertEqual(response, mock_request.return_value)

    @mock.patch("requests.api.request")
    def test_can_listener_http_verb_request_put(self, mock_request: mock.MagicMock) -> None:
        http_method = choices.HttpMethod.PUT
        response = http_method(self.url)

        mock_request.assert_called_once_with(http_method.value, self.url, data=None)
        self.assertEqual(response, mock_request.return_value)

    @mock.patch("requests.api.request")
    def test_can_listener_http_verb_request_delete(self, mock_request: mock.MagicMock) -> None:
        http_method = choices.HttpMethod.DELETE
        response = http_method(self.url)

        mock_request.assert_called_once_with(http_method.value, self.url)
        self.assertEqual(response, mock_request.return_value)
