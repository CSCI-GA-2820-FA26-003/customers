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
Test cases for Customer Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.models import Customer, DataValidationError, db
from .factories import CustomerFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BLANK_VALUES = [None, "", "   "]


######################################################################
#  Customer   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestCustomerModel(TestCase):
    """Test Cases for Customer Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()
        # Rebuild the schema so model changes apply without a migration
        db.drop_all()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Customer).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_customer(self):
        """It should create a customer"""
        customer = CustomerFactory()
        self.assertIsNone(customer.id)

        customer.create()

        self.assertIsNotNone(customer.id)
        found = Customer.all()
        self.assertEqual(len(found), 1)
        data = Customer.find(customer.id)
        self.assertEqual(data.name, customer.name)
        self.assertEqual(data.street, customer.street)
        self.assertEqual(data.city, customer.city)
        self.assertEqual(data.state, customer.state)
        self.assertEqual(data.postal_code, customer.postal_code)

    def test_update_customer(self):
        """It should update a customer"""
        customer = CustomerFactory()
        customer.create()
        new_name = "A whole new name"
        new_street = "A whole new street"
        original_id = customer.id

        customer.name = new_name
        customer.street = new_street
        customer.update()

        self.assertEqual(customer.id, original_id)
        found = Customer.find(customer.id)
        self.assertEqual(found.name, new_name)
        self.assertEqual(found.street, new_street)

    def test_delete_customer(self):
        """It should delete a customer"""
        customer = CustomerFactory()
        customer.create()

        customer.delete()

        found = Customer.find(customer.id)
        self.assertIsNone(found)

    def test_create_invalid_name(self):
        """It should not create a customer with no name or a blank name"""
        for value in BLANK_VALUES:
            with self.subTest(value=value):
                customer = CustomerFactory()
                customer.name = value

                self.assertRaises(DataValidationError, customer.create)

    def test_create_invalid_street(self):
        """It should not create a customer with no street or a blank street"""
        for value in BLANK_VALUES:
            with self.subTest(value=value):
                customer = CustomerFactory()
                customer.street = value

                self.assertRaises(DataValidationError, customer.create)

    def test_create_invalid_city(self):
        """It should not create a customer with no city or a blank city"""
        for value in BLANK_VALUES:
            with self.subTest(value=value):
                customer = CustomerFactory()
                customer.city = value

                self.assertRaises(DataValidationError, customer.create)

    def test_create_invalid_state(self):
        """It should not create a customer with no state or a blank state"""
        for value in BLANK_VALUES:
            with self.subTest(value=value):
                customer = CustomerFactory()
                customer.state = value

                self.assertRaises(DataValidationError, customer.create)

    def test_create_invalid_postal_code(self):
        """It should not create a customer with no postal code or a blank postal code"""
        for value in BLANK_VALUES:
            with self.subTest(value=value):
                customer = CustomerFactory()
                customer.postal_code = value

                self.assertRaises(DataValidationError, customer.create)

    def test_update_no_name(self):
        """It should not update a customer's name to none"""
        customer = CustomerFactory()
        customer.create()
        customer.name = None

        self.assertRaises(DataValidationError, customer.update)

    def test_update_no_street(self):
        """It should not update a customer's street to none"""
        customer = CustomerFactory()
        customer.create()
        customer.street = None

        self.assertRaises(DataValidationError, customer.update)

    def test_update_no_city(self):
        """It should not update a customer's city to none"""
        customer = CustomerFactory()
        customer.create()
        customer.city = None

        self.assertRaises(DataValidationError, customer.update)

    def test_update_no_state(self):
        """It should not update a customer's state to none"""
        customer = CustomerFactory()
        customer.create()
        customer.state = None

        self.assertRaises(DataValidationError, customer.update)

    def test_update_no_postal_code(self):
        """It should not update a customer's postal code to none"""
        customer = CustomerFactory()
        customer.create()
        customer.postal_code = None

        self.assertRaises(DataValidationError, customer.update)

    def test_update_no_id(self):
        """It should not update a customer without ID"""
        customer = CustomerFactory()
        customer.create()
        customer.id = None

        self.assertRaises(DataValidationError, customer.update)

    def test_delete_not_existing_customer(self):
        """It should not delete a customer that was never saved"""
        customer = CustomerFactory()

        self.assertRaises(DataValidationError, customer.delete)

    def test_serialize(self):
        """It should return a dictionary of a customer"""
        customer = CustomerFactory()

        data = customer.serialize()

        self.assertIsInstance(data, dict)
        self.assertEqual(data["id"], customer.id)
        self.assertEqual(data["name"], customer.name)
        self.assertEqual(data["street"], customer.street)
        self.assertEqual(data["city"], customer.city)
        self.assertEqual(data["state"], customer.state)
        self.assertEqual(data["postal_code"], customer.postal_code)
        self.assertNotIn("address", data)

    def test_deserialize(self):
        """It should return a model of a customer"""
        data = CustomerFactory().serialize()
        customer = Customer()

        customer.deserialize(data)

        self.assertEqual(customer.name, data["name"])
        self.assertEqual(customer.street, data["street"])
        self.assertEqual(customer.city, data["city"])
        self.assertEqual(customer.state, data["state"])
        self.assertEqual(customer.postal_code, data["postal_code"])

    def test_deserialize_invalid_data(self):
        """It should raise a data validation error"""
        data = CustomerFactory().serialize()
        del data["name"]
        customer = Customer()

        self.assertRaisesRegex(
            DataValidationError,
            "Invalid Customer: missing name",
            customer.deserialize,
            data,
        )

    def test_deserialize_invalid_data_type(self):
        """It should raise a data validation error"""
        data = []
        customer = Customer()

        self.assertRaisesRegex(
            DataValidationError,
            "Invalid Customer: body of request contained bad or no data ",
            customer.deserialize,
            data,
        )

    def test_deserialize_blank_fields(self):
        """It should not deserialize a blank or non-string field"""
        for field in ("name", "street", "city", "state", "postal_code"):
            for value in BLANK_VALUES + [12345]:
                with self.subTest(field=field, value=value):
                    data = CustomerFactory().serialize()
                    data[field] = value

                    self.assertRaisesRegex(
                        DataValidationError,
                        f"{field} must be a non-blank string",
                        Customer().deserialize,
                        data,
                    )

    def test_deserialize_invalid_state(self):
        """It should not deserialize an invalid state code"""
        for value in ["New York", "XX", "N", "NYC", " NY"]:
            with self.subTest(value=value):
                data = CustomerFactory().serialize()
                data["state"] = value

                self.assertRaisesRegex(
                    DataValidationError,
                    "invalid state code",
                    Customer().deserialize,
                    data,
                )

    def test_deserialize_lowercase_state(self):
        """It should store the state code uppercase"""
        data = CustomerFactory().serialize()
        data["state"] = "ny"

        customer = Customer().deserialize(data)

        self.assertEqual(customer.state, "NY")

    def test_deserialize_invalid_postal_code(self):
        """It should not deserialize an invalid postal code"""
        for value in ["ABCDE", "1234", "123456", "12345-678", "12345 6789", "12345\n"]:
            with self.subTest(value=value):
                data = CustomerFactory().serialize()
                data["postal_code"] = value

                self.assertRaisesRegex(
                    DataValidationError,
                    "invalid postal_code",
                    Customer().deserialize,
                    data,
                )

    def test_deserialize_zip_plus_four(self):
        """It should deserialize a ZIP+4 postal code"""
        data = CustomerFactory().serialize()
        data["postal_code"] = "10012-1234"

        customer = Customer().deserialize(data)

        self.assertEqual(customer.postal_code, "10012-1234")

    def test_all(self):
        """It should return a list of customer model"""
        customer1 = CustomerFactory()
        customer1.create()
        customer2 = CustomerFactory()
        customer2.create()
        customers = [customer1, customer2]

        found_list = Customer.all()

        self.assertEqual(len(found_list), 2)
        self.assertCountEqual(
            [c.serialize() for c in found_list],
            [c.serialize() for c in customers],
        )

    def test_find_by_id(self):
        """It should return a customer model"""
        customer = CustomerFactory()
        customer.create()

        found = Customer.find(customer.id)

        self.assertIsInstance(found, Customer)
        self.assertEqual(found.name, customer.name)
        self.assertEqual(found.street, customer.street)
        self.assertEqual(found.city, customer.city)
        self.assertEqual(found.state, customer.state)
        self.assertEqual(found.postal_code, customer.postal_code)

    def test_find_by_id_not_existing(self):
        """It should return None"""
        customer = CustomerFactory()
        customer.create()
        customer_id = customer.id
        customer.delete()

        found = Customer.find(customer_id)

        self.assertIsNone(found)

    def test_find_by_name(self):
        """It should return a customer model"""
        customer1 = CustomerFactory()
        customer1.create()
        customer2 = CustomerFactory()
        customer2.name = customer1.name
        customer2.create()
        customer3 = CustomerFactory()
        customer3.create()
        customers = [customer1, customer2]

        found_list = Customer.find_by_name(customer1.name)

        self.assertCountEqual(
            [c.serialize() for c in found_list.all()],
            [c.serialize() for c in customers],
        )
