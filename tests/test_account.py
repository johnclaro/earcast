import os
import unittest
import tempfile
import json

import pytest

from channelry import create_app
from channelry.models import db
from channelry.models.account import User

from libs import token

app = create_app('testing')
EMAIL = 'john@johndoedomainorigin.com'
FULLNAME = 'John Doe'
PASSWORD = 'johndoe12345'


class TestAccount(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all(app=self.app)

    def test_signup_and_login_and_details(self):
        response = self.client.post(
            '/signup',
            data=json.dumps({
                'email': EMAIL,
                'name': FULLNAME,
                'password': PASSWORD,
                'confirm': PASSWORD
            }),
            content_type='application/json'
        )
        assert response.status_code == 200, response.json

        response = self.client.post(
            '/login',
            data=json.dumps({
                'email': EMAIL,
                'password': PASSWORD
            }),
            content_type='application/json',
            headers={'Authorization': 'token'}
        )
        assert response.status_code == 200, response.json

        authorization = f"Bearer {response.json['accessToken']}"
        response = self.client.post(
            '/details',
            content_type='application/json',
            headers={'Authorization': authorization}
        )
        assert response.status_code == 200, response.json

    def test_signup_confirm_does_not_match_password(self):
        response = self.client.post(
            '/signup',
            data=json.dumps({
                'email': EMAIL,
                'name': FULLNAME,
                'password': PASSWORD,
                'confirm': 'iamawrongincorrectpassword'
            }),
            content_type='application/json'
        )
        assert response.status_code == 400, response.json
        assert response.json == {
            'field': 'confirm',
            'reason': 'Re-enter your password confirmation so it matches your password'
        }

    def test_confirm_email(self):
        confirmation_token = token.generate_confirmation_token(EMAIL)
        response = self.client.post(
            '/email/confirm',
            data=json.dumps({'confirmation_token': confirmation_token}),
            content_type='application/json'
        )
        assert response.status_code == 200, response.json


class TestUserModel(unittest.TestCase):

    def test_password_hash(self):
        user = User(EMAIL, PASSWORD, FULLNAME)
        assert len(user.password) == 60

    def test_password_match(self):
        user = User(EMAIL, PASSWORD, FULLNAME)
        assert user.password_match('johndoe12345')


if __name__ == '__main__':
    unittest.main()
