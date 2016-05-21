import unittest
from app.http_status_codes import *
from client import Client


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

class HTTPNotFound(BaseTest):
    def test_return_not_found(self):
        response = self.client.get('/unknown')
        self.assertEqual(response.status_code, HTTP_NOT_FOUND)

    def test_return_jsonified_error(self):
        response = self.client.get('/unknown')
        self.assertEqual(response.mimetype, 'application/json')
        self.assertIsInstance(response.json, dict)

class HTTPMethodNotAllowed(BaseTest):
    def test_return_method_not_allowed(self):
        response = self.client.patch('/resource/', data={})
        self.assertEqual(response.status_code, HTTP_METHOD_NOT_ALLOWED)

    def test_return_jsonfied_error(self):
        response = self.client.patch('/resource/', data={})
        self.assertEqual(response.mimetype, 'application/json')
        self.assertIsInstance(response.json, dict)

    def test_return_allowed_methods_header(self):
        response = self.client.patch('/resource/', data={})
        self.assertTrue(response.headers.has_key('Allow'))

if __name__ == '__main__':
    unittest.main()