import os
import unittest
import requests
import pytest

BASE_URL = os.environ.get("BASE_URL")

@pytest.mark.api
class TestReadOnlyApi(unittest.TestCase):

    def setUp(self):
        self.assertIsNotNone(BASE_URL)
        self.assertTrue(len(BASE_URL) > 8)

    def test_list_todos(self):
        response = requests.get(BASE_URL + "/todos")

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)