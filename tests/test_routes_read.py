"""Customer read and list route tests"""

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


class TestCustomerRead(TestCase):
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

    # TEST CASES

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
