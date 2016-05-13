import json
import unittest
import pymongo
from gimmejson import application
from app import database
from app.http_status_codes import HTTP_OK, HTTP_BAD_REQUEST
from settings import settings


class ResourceTest(unittest.TestCase):
    def setUp(self):
        database.connection.drop_database(settings.MONGODB_NAME)
        database.database[settings.MONGODB_COLLECTION_RESOURCE].create_index([('endpoint', pymongo.ASCENDING), ('methods', pymongo.ASCENDING)], unique=True)
        self.client = application.test_client()

    def tearDown(self):
        pass

    def test_get_all_resources(self):
        response = self.client.get('/resource')
        all_resources = json.loads(response.get_data())

        self.assertEqual(response.status_code, HTTP_OK)

    def test_create_new_resource(self):
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        response = self.client.post('/resource', data=json.dumps(payload), content_type='application/json')
        new_resource = json.loads(response.get_data())
        self.assertEqual(response.status_code, HTTP_OK)
        self.assertTrue(new_resource.has_key('_id'))

    def test_return_error_if_endpoint_missing_for_new_resource(self):
        """
        should return error if endpoint is missing when creating new resource
        """

        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "methods": [
              "GET"
            ]
        }

        response = self.client.post('/resource', data=json.dumps(payload), content_type='application/json')
        new_resource = json.loads(response.get_data())
        self.assertEqual(response.status_code, HTTP_BAD_REQUEST)
        self.assertTrue(new_resource.has_key('endpoint'))

    def test_return_error_if_response_missing(self):
        """
        should return error if response is missing when creating new resource
        """

        payload = {
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        response = self.client.post('/resource', data=json.dumps(payload), content_type='application/json')
        error = json.loads(response.get_data())

        self.assertEqual(response.status_code, HTTP_BAD_REQUEST)
        self.assertTrue(error.has_key('response'))

    def test_return_error_if_duplicate_endpoints_and_methods(self):
        """
        should return error if such endpoint and method is already exist when creating new resource
        """

        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "GET",
              "POST"
            ]
        }

        response = self.client.post('/resource', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, HTTP_OK)

        response = self.client.post('/resource', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, HTTP_BAD_REQUEST)

        error = json.loads(response.get_data())
        self.assertTrue(error.has_key('endpoint'))

    def test_return_error_if_methods_are_missing(self):
        """
        should return error if methods is missing when creating new resource
        """

        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test"
        }

        response = self.client.post('/resource', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, HTTP_BAD_REQUEST)

        error = json.loads(response.get_data())
        self.assertTrue(error.has_key('methods'))

    def test_return_error_if_all_fields_missing(self):
        payload = {}

        response = self.client.post('/resource', data=json.dumps(payload), content_type='application/json')
        error = json.loads(response.get_data())

        self.assertEqual(response.status_code, HTTP_BAD_REQUEST)

        response = self.client.post('/resource', data=None, content_type='application/json')

        self.assertEqual(response.status_code, HTTP_BAD_REQUEST)

    def test_delete_resource(self):
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        response = self.client.post('/resource', data=json.dumps(payload), content_type='application/json')
        new_resource = json.loads(response.get_data())
        new_resource_id = new_resource['_id']['$oid']
        response = self.client.delete('/resource/' + new_resource_id)
        self.assertEqual(response.status_code, HTTP_OK)

    def test_delete_unexistent_resource(self):
        response = self.client.delete('/resource/' + '571b7cfdeceefb4a395ef433')
        self.assertTrue(response.status_code, HTTP_BAD_REQUEST)

    def test_should_patch_all_fields(self):
        """
        should patch all available fields
        """

        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        response = self.client.post('/resource', data=json.dumps(payload), content_type='application/json')
        new_resource = json.loads(response.get_data())
        resource_id = new_resource['_id']['$oid']

        new_payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Tel-Aviv\"}",
            "endpoint": "/api/v1/people",
            "methods": [
              "POST"
            ]
        }

        response = self.client.patch('/resource/' + resource_id, data=json.dumps(new_payload), content_type='application/json')
        patched_resource = json.loads(response.get_data())
        new_payload['_id'] = patched_resource['_id']

        self.assertEqual(response.status_code, HTTP_OK)
        self.assertEqual(patched_resource, new_payload)

    def test_return_error_if_duplicate_endpoints_and_methods_on_modification(self):
        """
        should return error if such endpoint and methods already exist
        when trying to modify existing endpoint
        """
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        payload_second = {
            "response": "{\"name\": \"Bob\"}",
            "endpoint": "/api/v1/people",
            "methods": [
              "GET"
            ]
        }

        self.client.post('/resource', data=json.dumps(payload), content_type='application/json')
        response = self.client.post('/resource', data=json.dumps(payload_second), content_type='application/json')

        resource_to_patch = json.loads(response.get_data())
        resource_id = resource_to_patch['_id']['$oid']

        resource_to_patch['endpoint'] = '/api/v1/test'

        response = self.client.patch('/resource/' + resource_id, data=json.dumps(resource_to_patch), content_type='application/json')
        error = json.loads(response.get_data())

        self.assertEqual(response.status_code, HTTP_BAD_REQUEST)
        self.assertTrue(error.has_key('endpoint'))

    def test_return_error_if_patching_id(self):
        """
        should return error when trying to patch resource id
        """

        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        response = self.client.post('/resource', data=json.dumps(payload), content_type='application/json')
        new_resource = json.loads(response.get_data())
        resource_id = new_resource['_id']['$oid']

        patch_payload = {
            '_id': {'$oid': '571b7cfdeceefb4a395ef433'}
        }

        response = self.client.patch('/resource/' + resource_id, data=json.dumps(patch_payload), content_type='application/json')

        self.assertTrue(response.status_code, HTTP_BAD_REQUEST)

    def test_should_put_successfully(self):
        """
        PUT
        """
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        response = self.client.post('/resource', data=json.dumps(payload), content_type='application/json')
        new_resource_id = json.loads(response.get_data())['_id']['$oid']

        payload['methods'] = ['POST']
        response = self.client.put('/resource/' + new_resource_id, data=json.dumps(payload), content_type='application/json')
        updated_resource = json.loads(response.get_data())
        self.assertEqual(updated_resource['methods'], ['POST'])

    def test_should_ignore_id_on_put(self):
        """
        PUT
        """
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        response = self.client.post('/resource', data=json.dumps(payload), content_type='application/json')
        new_resource_id = json.loads(response.get_data())
        payload['methods'] = ['POST']
        payload['_id'] = new_resource_id

        response = self.client.put('/resource/' + new_resource_id['_id']['$oid'], data=json.dumps(payload), content_type='application/json')

        self.assertEqual(response.status_code, HTTP_OK)

    def test_return_an_error_if_duplicates_when_put(self):
        """
        PUT
        """
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        another_payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "POST"
            ]
        }

        response = self.client.post('/resource', data=json.dumps(payload), content_type='application/json')
        new_resource_id = json.loads(response.get_data())['_id']['$oid']
        self.assertEqual(response.status_code, HTTP_OK)

        response = self.client.post('/resource', data=json.dumps(another_payload), content_type='application/json')
        new_resource_id = json.loads(response.get_data())['_id']['$oid']
        self.assertEqual(response.status_code, HTTP_OK)

        another_payload['methods'] = ['GET']
        response = self.client.put('/resource/' + new_resource_id, data=json.dumps(another_payload), content_type='application/json')
        self.assertEqual(response.status_code, HTTP_BAD_REQUEST)

    def test_return_error_if_all_fields_missing_on_put(self):
        """
        PUT
        """
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        response = self.client.post('/resource', data=json.dumps(payload), content_type='application/json')
        new_resource_id = json.loads(response.get_data())['_id']['$oid']

        empty_payload = {}
        response = self.client.put('/resource/' + new_resource_id, data=json.dumps(empty_payload), content_type='application/json')
        self.assertEqual(response.status_code, HTTP_BAD_REQUEST)

    def test_return_error_if_response_missing_on_put(self):
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        response = self.client.post('/resource', data=json.dumps(payload), content_type='application/json')
        new_resource_id = json.loads(response.get_data())['_id']['$oid']

        del payload['response']
        response = self.client.put('/resource/' + new_resource_id, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, HTTP_BAD_REQUEST)

    def test_return_error_if_methods_missing_on_put(self):
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        response = self.client.post('/resource', data=json.dumps(payload), content_type='application/json')
        new_resource_id = json.loads(response.get_data())['_id']['$oid']

        del payload['methods']
        response = self.client.put('/resource/' + new_resource_id, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, HTTP_BAD_REQUEST)

    def test_return_error_if_endpoint_missing_on_put(self):
        payload = {
            "response": "{\"name\": \"Alice\", \"city\": \"Berlin\"}",
            "endpoint": "/api/v1/test",
            "methods": [
              "GET"
            ]
        }

        response = self.client.post('/resource', data=json.dumps(payload), content_type='application/json')
        new_resource_id = json.loads(response.get_data())['_id']['$oid']

        del payload['endpoint']
        response = self.client.put('/resource/' + new_resource_id, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, HTTP_BAD_REQUEST)

if __name__ == '__main__':
    unittest.main()