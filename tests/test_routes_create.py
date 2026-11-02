"""Customer create route tests"""

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


class TestCustomerCreate(TestCase):
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
