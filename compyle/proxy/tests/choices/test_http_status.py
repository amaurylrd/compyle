# pylint: disable=missing-function-docstring

from unittest import mock

import requests
from django.test import TestCase

from compyle.proxy import choices


class TestHttpStatus(TestCase):
    """TestCase for the `HttpStatus` enum in the choices module."""

    def setUp(self) -> None:  # pylint: disable=invalid-name
        super().setUp()

    def test_informational_status(self) -> None:
        self.assertEqual(choices.HttpStatus.from_status_code(100), choices.HttpStatus.INFORMATIONAL)
        self.assertEqual(choices.HttpStatus.from_status_code(199), choices.HttpStatus.INFORMATIONAL)

    def test_success_status(self) -> None:
        self.assertEqual(choices.HttpStatus.from_status_code(200), choices.HttpStatus.SUCCESS)
        self.assertEqual(choices.HttpStatus.from_status_code(299), choices.HttpStatus.SUCCESS)

    def test_redirect_status(self) -> None:
        self.assertEqual(choices.HttpStatus.from_status_code(300), choices.HttpStatus.REDIRECT)
        self.assertEqual(choices.HttpStatus.from_status_code(399), choices.HttpStatus.REDIRECT)

    def test_client_error_status(self) -> None:
        self.assertEqual(choices.HttpStatus.from_status_code(400), choices.HttpStatus.CLIENT_ERROR)
        self.assertEqual(choices.HttpStatus.from_status_code(499), choices.HttpStatus.CLIENT_ERROR)

    def test_server_error_status(self) -> None:
        self.assertEqual(choices.HttpStatus.from_status_code(500), choices.HttpStatus.SERVER_ERROR)
        self.assertEqual(choices.HttpStatus.from_status_code(599), choices.HttpStatus.SERVER_ERROR)

    def test_unknown_status_code(self) -> None:
        self.assertIsNone(choices.HttpStatus.from_status_code(99))
        self.assertIsNone(choices.HttpStatus.from_status_code(600))
