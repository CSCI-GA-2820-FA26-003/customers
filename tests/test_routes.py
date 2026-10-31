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
        # Rebuild the schema so model changes apply without a migration
        db.drop_all()
        db.create_all()

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

    def test_read_customer(self):
        """It should read a customer by ID"""
        customer = CustomerFactory()
        customer.create()

        response = self.client.get(f"/customers/{customer.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.is_json)
        self.assertEqual(response.get_json(), customer.serialize())

    def test_read_customer_not_found(self):
        """It should return 404 for a missing customer"""
        response = self.client.get("/customers/999999")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(response.is_json)
        self.assertEqual(response.get_json()["error"], "Not Found")

    # CREATE CUSTOMER TEST CASES

    def test_create_customer(self):
        """It should create a new customer"""
        test_customer = CustomerFactory()
        response = self.client.post(BASE_URL, json=test_customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.headers.get("Location"))
        new_customer = response.get_json()
        self.assertEqual(new_customer["name"], test_customer.name)
        self.assertEqual(new_customer["street"], test_customer.street)
        self.assertEqual(new_customer["city"], test_customer.city)
        self.assertEqual(new_customer["state"], test_customer.state)
        self.assertEqual(new_customer["postal_code"], test_customer.postal_code)
        self.assertEqual(new_customer["membership_level"], "bronze")

    def test_create_customer_default_membership_level(self):
        """It should create a new customer with bronze membership level by default"""
        data = CustomerFactory().serialize()
        del data["membership_level"]
        response = self.client.post(BASE_URL, json=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.get_json()["membership_level"], "bronze")

    def test_create_customer_ignores_membership_level(self):
        """It should create a new customer with bronze even if another level is given"""
        data = CustomerFactory().serialize()
        data["membership_level"] = "gold"
        response = self.client.post(BASE_URL, json=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_customer = response.get_json()
        self.assertEqual(new_customer["membership_level"], "bronze")
        self.assertEqual(Customer.find(new_customer["id"]).membership_level, "bronze")

    def test_create_customer_invalid_membership_level(self):
        """It should not create a customer with an unknown membership level"""
        data = CustomerFactory().serialize()
        data["membership_level"] = "platinum"
        response = self.client.post(BASE_URL, json=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_customer_no_street(self):
        """It should not create a customer without a street"""
        test_customer = CustomerFactory()
        data = test_customer.serialize()
        del data["street"]
        response = self.client.post(BASE_URL, json=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_customer_no_city(self):
        """It should not create a customer without a city"""
        test_customer = CustomerFactory()
        data = test_customer.serialize()
        del data["city"]
        response = self.client.post(BASE_URL, json=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_customer_no_state(self):
        """It should not create a customer without a state"""
        test_customer = CustomerFactory()
        data = test_customer.serialize()
        del data["state"]
        response = self.client.post(BASE_URL, json=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_customer_no_postal_code(self):
        """It should not create a customer without a postal code"""
        test_customer = CustomerFactory()
        data = test_customer.serialize()
        del data["postal_code"]
        response = self.client.post(BASE_URL, json=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_customer_invalid_state(self):
        """It should not create a customer with an invalid state code"""
        data = CustomerFactory().serialize()
        data["state"] = "New York"
        response = self.client.post(BASE_URL, json=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_customer_invalid_postal_code(self):
        """It should not create a customer with an invalid postal code"""
        data = CustomerFactory().serialize()
        data["postal_code"] = "ABCDE"
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
        customer.membership_level = "bronze"
        customer.create()

        customer_id = customer.id
        new_name = "Updated Name"
        new_street = "Updated Street"
        updated_data = customer.serialize()
        updated_data["name"] = new_name
        updated_data["street"] = new_street
        updated_data["membership_level"] = "gold"

        resp = self.client.put(f"/customers/{customer_id}", json=updated_data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json["id"], customer_id)
        self.assertEqual(resp.json["name"], new_name)
        self.assertEqual(resp.json["street"], new_street)
        self.assertEqual(resp.json["membership_level"], "gold")
        self.assertEqual(Customer.find(customer_id).membership_level, "gold")

    def test_update_customer_not_found(self):
        """It should return 404 Not Found when updating a non-existent customer"""
        non_existent_id = 9999
        updated_data = CustomerFactory().serialize()

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
        invalid_data = {
            "name": None,
            "street": None,
            "city": None,
            "state": None,
            "postal_code": None,
        }

        resp = self.client.put(f"/customers/{customer_id}", json=invalid_data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", resp.json)

    # DELETE CUSTOMER TEST CASES

    def test_delete_customer(self):
        """It should delete an existing customer"""
        test_customer = CustomerFactory()
        response = self.client.post(BASE_URL, json=test_customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        customer_id = response.get_json()["id"]

        response = self.client.delete(f"{BASE_URL}/{customer_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        self.assertIsNone(Customer.find(customer_id))

    def test_delete_nonexistent_customer(self):
        """It should return 204 when deleting a customer that does not exist"""
        response = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

    ######################################################################
    #  LIST   T E S T   C A S E S
    ######################################################################

    def test_list_customers_with_data_in_database(self):
        """It should return a list of customers"""
        customer_data = []
        for i in range(5):
            customer_data.append(CustomerFactory())
            customer_data[i].create()
            customer_data[i] = customer_data[i].serialize()

        resp = self.client.get("/customers")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertCountEqual(resp.get_json(), customer_data)

    def test_list_customers_with_no_data_in_database(self):
        """It should return an empty list"""
        resp = self.client.get("/customers")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get_json(), [])

    ######################################################################
    #  U P G R A D E   T E S T   C A S E S
    ######################################################################

    def test_upgrade_customer(self):
        """It should upgrade a customer's membership level"""
        customer = CustomerFactory()
        customer.create()

        response = self.client.put(
            f"/customers/{customer.id}/upgrade", json={"target_level": "gold"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_json()["id"], customer.id)
        self.assertEqual(response.get_json()["membership_level"], "gold")

    def test_upgrade_customer_invalid_level(self):
        """It should reject an unknown membership level"""
        customer = CustomerFactory()
        customer.create()

        response = self.client.put(
            f"/customers/{customer.id}/upgrade", json={"target_level": "Premium"}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid membership level", response.get_json()["message"])

    def test_upgrade_customer_cannot_downgrade(self):
        """It should reject downgrading through the upgrade endpoint"""
        customer = CustomerFactory()
        customer.membership_level = "gold"
        customer.create()

        response = self.client.put(
            f"/customers/{customer.id}/upgrade", json={"target_level": "silver"}
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn(
            "Cannot downgrade membership via upgrade action",
            response.get_json()["message"],
        )

    def test_upgrade_customer_not_found(self):
        """It should return 404 after the customer has been deleted"""
        customer = CustomerFactory()
        customer.create()
        customer_id = customer.id
        customer.delete()

        response = self.client.put(
            f"/customers/{customer_id}/upgrade", json={"target_level": "silver"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # DOWNGRADE TEST CASES

    def test_downgrade_customer(self):
        """It should downgrade a customer's membership level"""
        customer = CustomerFactory()
        customer.membership_level = "gold"
        customer.create()

        response = self.client.put(
            f"/customers/{customer.id}/downgrade", json={"target_level": "bronze"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_json()["id"], customer.id)
        self.assertEqual(response.get_json()["membership_level"], "bronze")

    def test_downgrade_customer_cannot_upgrade(self):
        """It should reject upgrading through the downgrade endpoint"""
        customer = CustomerFactory()
        customer.membership_level = "bronze"
        customer.create()

        response = self.client.put(
            f"/customers/{customer.id}/downgrade", json={"target_level": "gold"}
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn(
            "Cannot upgrade membership via downgrade action",
            response.get_json()["message"],
        )

    def test_downgrade_customer_invalid_level(self):
        """It should reject an unknown membership level"""
        customer = CustomerFactory()
        customer.membership_level = "gold"
        customer.create()

        response = self.client.put(
            f"/customers/{customer.id}/downgrade", json={"target_level": "Premium"}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid membership level", response.get_json()["message"])

    def test_downgrade_customer_not_found(self):
        """It should return 404 when the customer does not exist"""
        response = self.client.put(
            "/customers/0/downgrade", json={"target_level": "bronze"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
