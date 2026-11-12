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

    def test_query_customers_by_single_field(self):
        """It should filter by state, membership level, postal code, or name."""
        matching = CustomerFactory(
            state="NY",
            postal_code="10012",
            membership_level="gold",
            last_name="first_name",
            first_name="last_name",
        )
        matching.create()
        CustomerFactory(
            state="CA",
            postal_code="90001",
            membership_level="bronze",
        ).create()

        for filters in (
            {"state": "ny"},
            {"membership_level": "gold"},
            {"postal_code": "10012"},
            {"last_name": "first_name"},
            {"first_name": "last_name"},
        ):
            with self.subTest(filters=filters):
                response = self.client.get("/customers", query_string=filters)

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.get_json(), [matching.serialize()])

    def test_query_customers_by_combined_filters(self):
        """It should match every supplied filter."""
        matching = CustomerFactory(city="Albany", state="NY", membership_level="gold")
        matching.create()
        CustomerFactory(city="Albany", state="GA", membership_level="gold").create()
        CustomerFactory(city="Albany", state="NY", membership_level="bronze").create()

        response = self.client.get(
            "/customers",
            query_string={
                "city": "Albany",
                "state": "NY",
                "membership_level": "gold",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_json(), [matching.serialize()])

    def test_query_customers_city_requires_state(self):
        """It should reject a city query without a state."""
        response = self.client.get("/customers", query_string={"city": "Albany"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("state is required", response.get_json()["message"])

    def test_query_customers_no_match(self):
        """It should return an empty list when no customers match."""
        CustomerFactory(state="NY").create()

        response = self.client.get("/customers", query_string={"state": "CA"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_json(), [])

    def test_query_customers_invalid_values(self):
        """It should reject invalid filter values."""
        for field, value in (
            ("state", "XX"),
            ("membership_level", "platinum"),
            ("postal_code", "123"),
        ):
            with self.subTest(field=field):
                response = self.client.get("/customers", query_string={field: value})

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(f"invalid {field}", response.get_json()["message"])

    def test_query_customers_blank_values(self):
        """It should reject empty or whitespace-only filter values."""
        for field in (
            "city",
            "state",
            "membership_level",
            "postal_code",
            "last_name",
            "first_name",
        ):
            for value in ("", "   "):
                with self.subTest(field=field, value=value):
                    response = self.client.get(
                        "/customers", query_string={field: value}
                    )

                    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                    self.assertIn(
                        f"{field} must not be blank",
                        response.get_json()["message"],
                    )
