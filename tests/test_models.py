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
        self.assertEqual(data.address, customer.address)

    def test_update_customer(self):
        """It should update a customer"""
        customer = CustomerFactory()
        customer.create()
        new_name = "A whole new name"
        new_address = "A whole new address"

        customer.name = new_name
        customer.address = new_address
        customer.update()

        found = Customer.find(customer.id)
        self.assertEqual(found.name, new_name)
        self.assertEqual(found.address, new_address)

    def test_delete_customer(self):
        """It should delete a customer"""
        customer = CustomerFactory()
        customer.create()

        customer.delete()

        found = Customer.find(customer.id)
        self.assertIsNone(found)

    def test_create_no_name(self):
        """It should not create a customer with no name"""
        customer = CustomerFactory()
        customer.name = None

        self.assertRaises(DataValidationError, customer.create)

    def test_create_no_address(self):
        """It should not create a customer with no address"""
        customer = CustomerFactory()
        customer.address = None

        self.assertRaises(DataValidationError, customer.create)

    def test_update_no_name(self):
        """It should not update a customer's name to none"""
        customer = CustomerFactory()
        customer.create()
        customer.name = None

        self.assertRaises(DataValidationError, customer.update)

    def test_update_no_address(self):
        """It should not update a customer's address to none"""
        customer = CustomerFactory()
        customer.create()
        customer.address = None

        self.assertRaises(DataValidationError, customer.update)

    def test_update_no_id(self):
        """It should not update a customer without ID"""
        customer = CustomerFactory()
        customer.create()
        customer.id = None

        self.assertRaises(DataValidationError, customer.update)

    def test_delete_not_existing_customer(self):
        """It should delete a"""
        customer = CustomerFactory()
        customer.create()

        self.assertRaises(DataValidationError, customer.delete)

    def test_serialize(self):
        """It should return a dictionary of a customer"""
        customer = CustomerFactory()

        data = customer.serialize()

        self.assertIsInstance(data, dict)
        self.assertEqual(data["id"], customer.id)
        self.assertEqual(data["name"], customer.name)
        self.assertEqual(data["address"], customer.address)

    def test_deserialize(self):
        """It should return a model of a customer"""
        data = CustomerFactory().serialize()
        customer = Customer()

        customer.deserialize(data)

        self.assertEqual(customer.name, data["name"])
        self.assertEqual(customer.address, data["address"])

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
        self.assertEqual(found.address, customer.address)

    def test_find_by_id_not_existing(self):
        """It should return None"""
        customer = CustomerFactory()
        self.assertRaises(DataValidationError, customer.delete)

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
