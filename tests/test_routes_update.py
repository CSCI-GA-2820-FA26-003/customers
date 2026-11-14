"""Customer update route tests"""

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


class TestCustomerUpdate(TestCase):
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

    # UPDATE TEST CASES

    def test_update_customer(self):
        """It should update a customer with valid info and return 200 OK"""
        customer = CustomerFactory()
        customer.membership_level = "bronze"
        customer.create()

        customer_id = customer.id
        new_first_name = "Updated First Name"
        new_last_name = "Updated Last Name"
        new_street = "Updated Street"
        updated_data = customer.serialize()
        updated_data["first_name"] = new_first_name
        updated_data["last_name"] = new_last_name
        updated_data["street"] = new_street

        resp = self.client.put(f"/customers/{customer_id}", json=updated_data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_data, resp.get_json())

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
            "first_name": None,
            "last_name": None,
            "street": None,
            "city": None,
            "state": None,
            "postal_code": None,
            "email": None,
        }

        resp = self.client.put(f"/customers/{customer_id}", json=invalid_data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", resp.json)

    def test_update_customer_email(self):
        """It should update a customer's email"""
        customer = CustomerFactory()
        customer.create()
        updated_data = customer.serialize()
        updated_data["email"] = "new.email@example.com"

        resp = self.client.put(f"/customers/{customer.id}", json=updated_data)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get_json()["email"], "new.email@example.com")
        self.assertEqual(Customer.find(customer.id).email, "new.email@example.com")

    def test_update_customer_no_email(self):
        """It should return 400 Bad Request when the email is missing"""
        customer = CustomerFactory()
        customer.create()
        updated_data = customer.serialize()
        del updated_data["email"]

        resp = self.client.put(f"/customers/{customer.id}", json=updated_data)

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("missing email", resp.get_json()["message"])

    def test_update_customer_invalid_email(self):
        """It should return 400 Bad Request and keep the email when it is invalid"""
        customer = CustomerFactory()
        customer.create()
        original_email = customer.email
        updated_data = customer.serialize()
        updated_data["email"] = "not-an-email"

        resp = self.client.put(f"/customers/{customer.id}", json=updated_data)

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("invalid email", resp.get_json()["message"])
        self.assertEqual(Customer.find(customer.id).email, original_email)

    def test_update_customer_duplicate_email(self):
        """It should return 409 Conflict when the email belongs to another customer"""
        other = CustomerFactory()
        other.create()
        customer = CustomerFactory()
        customer.create()
        original_email = customer.email
        updated_data = customer.serialize()
        updated_data["email"] = other.email

        resp = self.client.put(f"/customers/{customer.id}", json=updated_data)

        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
        self.assertIn(other.email, resp.get_json()["message"])
        self.assertEqual(Customer.find(customer.id).email, original_email)

    # UPGRADE TEST CASES

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
