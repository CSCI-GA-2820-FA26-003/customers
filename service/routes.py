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

from flask import jsonify, request, abort, url_for
from flask import current_app as app  # Import Flask application

from service.models import (
    Customer,
    MEMBERSHIP_LEVELS,
    POSTAL_CODE_PATTERN,
    US_STATE_CODES,
)
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Customer REST API Service",
            version="1.0",
            description=(
                "Create, read, update, delete and list the customers "
                "that are registered in the e-commerce store"
            ),
            paths=url_for("list_customers", _external=True)
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

@app.route("/customers/<int:customer_id>", methods=["GET"])
def read_customer(customer_id):
    """Read a customer by ID"""
    app.logger.info("Request to read customer with id: %s", customer_id)

    customer = Customer.find(customer_id)
    if customer is None:
        abort(
            status.HTTP_404_NOT_FOUND,
            description=f"Customer with id {customer_id} was not found",
        )

    return jsonify(customer.serialize()), status.HTTP_200_OK


# CREATE A NEW CUSTOMER
@app.route("/customers", methods=["POST"])
def create_customers():
    """Create a Customer"""
    app.logger.info("Request to Create a Customer...")
    data = request.get_json()
    customer = Customer()
    customer.deserialize(data)
    # Every new customer starts at bronze; the level can only be changed by an update
    customer.membership_level = "bronze"
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


# DELETE A CUSTOMER
@app.route("/customers/<int:customer_id>", methods=["DELETE"])
def delete_customers(customer_id):
    """Delete a Customer
    This endpoint will delete a Customer based on the id specified in the path
    """
    app.logger.info("Request to Delete a customer with id [%s]", customer_id)

    customer = Customer.find(customer_id)
    if customer:
        customer.delete()
        app.logger.info("Customer with id [%s] was deleted", customer_id)

    return "", status.HTTP_204_NO_CONTENT


# list all customers
@app.route("/customers", methods=["GET"])
def list_customers():
    """List customers with optional query filters."""
    app.logger.info("Request to list all customers")
    query = Customer.query

    if "membership_level" in request.args:
        membership_level = request.args["membership_level"].lower()
        if membership_level not in MEMBERSHIP_LEVELS:
            abort(
                status.HTTP_400_BAD_REQUEST,
                description="Invalid membership_level",
            )
        query = query.filter(Customer.membership_level == membership_level)

    if "state" in request.args:
        state = request.args["state"].upper()
        if state not in US_STATE_CODES:
            abort(
                status.HTTP_400_BAD_REQUEST,
                description="Invalid state code",
            )
        query = query.filter(Customer.state == state)

    if "city" in request.args:
        query = query.filter(Customer.city == request.args["city"])

    if "postal_code" in request.args:
        postal_code = request.args["postal_code"]
        if not POSTAL_CODE_PATTERN.fullmatch(postal_code):
            abort(
                status.HTTP_400_BAD_REQUEST,
                description="Invalid postal_code",
            )
        query = query.filter(Customer.postal_code == postal_code)

    customers = query.all()

    results = [customer.serialize() for customer in customers]
    app.logger.info("Returning %d customers", len(results))
    return jsonify(results), status.HTTP_200_OK
