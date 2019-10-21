# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_emails.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>', 'David Matthews <@tree1004>']
__status__ = 'development'
__date__ = '2019.07.23'

import time
import unittest

from sim_api.token import (
    URLTokenError, URLTokenExpired, confirm_token, generate_confirmation_token,
    generate_url
)
from tests.test_api_base import BaseTestCase


class TestTokenURL(BaseTestCase):
    def test_verify_token(self):
        """Ensure that both confirm token encoding and decoding work."""
        token = generate_confirmation_token('dummy@email.com')
        email = confirm_token(token)
        self.assertEqual(email, 'dummy@email.com')

    def test_verify_invalid_token(self):
        """Ensure an invalid token will not be decoded."""
        invalid_token = 'invalid string'
        with self.assertRaises(URLTokenError):
            email = confirm_token(invalid_token)
            self.assertEqual(email, False)

    def test_verify_expired_token(self):
        """Ensure that if the token is expired it fails."""
        token = generate_confirmation_token('dummy@email.com')
        time.sleep(1)
        with self.assertRaises(URLTokenExpired):
            email = confirm_token(token, 0)
            self.assertEqual(email, False)

    def test_token_is_unique(self):
        """Ensure tokens are unique."""
        token1 = generate_confirmation_token('dummy@email.com')
        token2 = generate_confirmation_token('dummy@email2.com')
        self.assertNotEqual(token1, token2)

    def test_generate_url(self):
        """Ensure generate_url behaves as expected."""
        token = generate_confirmation_token('dummy@email.com')
        url = generate_url('auth.confirm_email', token)
        url_token = url.split('/')[6]
        self.assertEqual(token, url_token)
        email = confirm_token(url_token)
        self.assertEqual(email, 'dummy@email.com')


if __name__ == '__main__':
    unittest.main()

#
