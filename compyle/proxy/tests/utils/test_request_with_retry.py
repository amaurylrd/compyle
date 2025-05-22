# pylint: disable=missing-function-docstring

from unittest import mock

from django.test import SimpleTestCase
from requests.auth import HTTPBasicAuth
from requests.models import Response
from rest_framework import status

from compyle.proxy import utils
from compyle.proxy.choices import HttpMethod


class TestRequest(SimpleTestCase):
    """TestCase for the `request_with_retry` method in the utils module."""

    maxDiff = None

    def setUp(self) -> None:  # pylint: disable=invalid-name
        super().setUp()

        self.url = "https://example.com"

    @mock.patch("requests.Session.request")
    def test_successful_request(self, mock_request: mock.MagicMock) -> None:
        mock_response = mock.MagicMock(spec=Response)
        mock_response.status_code = status.HTTP_200_OK
        mock_response.text = "Success"
        mock_request.return_value = mock_response

        response = utils.request_with_retry(HttpMethod.GET, self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.text, "Success")
        mock_request.assert_called_once_with(
            method=HttpMethod.GET.value,
            url="https://example.com",
            params=None,
            timeout=None,
        )

    @mock.patch("requests.Session.request")
    def test_request_passes_timeout(self, mock_request: mock.MagicMock) -> None:
        mock_auth = mock.Mock(spec=HTTPBasicAuth)

        mock_response = mock.MagicMock(spec=Response)
        mock_response.status_code = status.HTTP_200_OK
        mock_request.return_value = mock_response

        headers = {"Authorization": "Bearer token"}
        data = {"title": "example"}

        utils.request_with_retry(
            HttpMethod.POST,
            self.url,
            headers=headers,
            data=data,
            auth=mock_auth,
            timeout=10.0,
        )

        mock_request.assert_called_once_with(
            method=HttpMethod.POST.value,
            url=self.url,
            data=data,
            json=None,
            headers=headers,
            auth=mock_auth,
            timeout=10.0,
        )
