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
Customer Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Customer
"""

# from flask import jsonify, request, url_for, abort
from flask import jsonify, request, abort
from flask import current_app as app  # Import Flask application

from service.models import Customer
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


# CREATE A NEW CUSTOMER
@app.route("/customers", methods=["POST"])
def create_customers():
    """Create a Customer"""
    app.logger.info("Request to Create a Customer...")
    data = request.get_json()
    customer = Customer()
    customer.deserialize(data)
    customer.create()
    app.logger.info("Customer with new id [%s] created.", customer.id)
    location_url = f"{request.base_url}/{customer.id}"
    return (
        jsonify(customer.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


# update customer
@app.route("/customers/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id):
    """Update a Customer"""
    app.logger.info("Request to update customer with id: %s", customer_id)
    customer = Customer.find(customer_id)
    if not customer:
        abort(status.HTTP_404_NOT_FOUND)

    data = request.get_json()
    customer.deserialize(data)
    customer.update()

    app.logger.info("Customer with id %s updated successfully", customer_id)
    return jsonify(customer.serialize()), status.HTTP_200_OK


# update customer
@app.route("/customers", methods=["GET"])
def list_customers():
    """List All Customers"""
    app.logger.info("Request to list all customers")
    customers = Customer.all()

    results = [customer.serialize() for customer in customers]
    app.logger.info("Returning %d customers", len(results))
    return jsonify(results), status.HTTP_200_OK
