######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
TestYourResourceModel API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Customer
from .factories import CustomerFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/customers"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestCustomerService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Customer).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page and return a 200 OK with service information"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.is_json)
        data = resp.get_json()
        self.assertEqual(data["name"], "Customer REST API Service")
        self.assertEqual(data["version"], "1.0")
        self.assertIn("description", data)
        self.assertTrue(data["paths"].endswith("/customers"))

    def test_index_method_not_allowed(self):
        """It should return a 405 when the root URL is called with a method that is not allowed"""
        resp = self.client.post("/")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertTrue(resp.is_json)
        self.assertIn("message", resp.get_json())

    # CREATE CUSTOMER TEST CASES

    def test_create_customer(self):
        """It should create a new customer"""
        test_customer = CustomerFactory()
        response = self.client.post(BASE_URL, json=test_customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.headers.get("Location"))
        new_customer = response.get_json()
        self.assertEqual(new_customer["name"], test_customer.name)
        self.assertEqual(new_customer["address"], test_customer.address)

    def test_create_customer_no_address(self):
        """It should not create a customer without an address"""
        test_customer = CustomerFactory()
        data = test_customer.serialize()
        del data["address"]
        response = self.client.post(BASE_URL, json=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_customer_wrong_content_type(self):
        """It should not create a customer with the wrong content type"""
        response = self.client.post(BASE_URL, data="hello", content_type="text/plain")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_method_not_allowed(self):
        """It should return 405 for a method that is not allowed"""
        response = self.client.post("/")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_not_found(self):
        """It should return 404 for a URL that does not exist"""
        response = self.client.get("/nonexistent")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    #  U P D A T E   T E S T   C A S E S
    ######################################################################

    def test_update_customer(self):
        """It should update a customer with valid info and return 200 OK"""
        customer = CustomerFactory()
        customer.create()

        customer_id = customer.id
        new_name = "Updated Name"
        new_address = "Updated Address"
        updated_data = {"name": new_name, "address": new_address}

        resp = self.client.put(f"/customers/{customer_id}", json=updated_data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json["id"], customer_id)
        self.assertEqual(resp.json["name"], new_name)
        self.assertEqual(resp.json["address"], new_address)

    def test_update_customer_not_found(self):
        """It should return 404 Not Found when updating a non-existent customer"""
        non_existent_id = 9999
        updated_data = {"name": "New Name", "address": "New Address"}

        resp = self.client.put(f"/customers/{non_existent_id}", json=updated_data)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", resp.json)

    def test_update_customer_no_data(self):
        """It should return 400 Bad Request when no data is provided"""
        customer = CustomerFactory()
        customer.create()

        customer_id = customer.id

        resp = self.client.put(f"/customers/{customer_id}", json={})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", resp.json)

    def test_update_customer_invalid_data(self):
        """It should return 400 Bad Request when invalid data is provided"""
        customer = CustomerFactory()
        customer.create()

        customer_id = customer.id
        invalid_data = {"name": None, "address": None}  # Invalid data

        resp = self.client.put(f"/customers/{customer_id}", json=invalid_data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", resp.json)
