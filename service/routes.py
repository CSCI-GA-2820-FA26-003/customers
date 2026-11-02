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

from service.models import Customer, MEMBERSHIP_LEVELS
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
            paths=url_for("list_customers", _external=True),
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
    """List All Customers"""
    app.logger.info("Request to list all customers")
    customers = Customer.all()

    results = [customer.serialize() for customer in customers]
    app.logger.info("Returning %d customers", len(results))
    return jsonify(results), status.HTTP_200_OK


# upgrade a customer's membership
@app.route("/customers/<int:customer_id>/upgrade", methods=["PUT"])
def upgrade_customer(customer_id):
    """Upgrade a customer's membership level without allowing downgrades."""
    app.logger.info("Request to upgrade customer with id: %s", customer_id)

    customer = Customer.find(customer_id)
    if customer is None:
        abort(status.HTTP_404_NOT_FOUND)

    data = request.get_json()
    target_level = data.get("target_level") if isinstance(data, dict) else None
    if (
        not isinstance(target_level, str)
        or target_level.lower() not in MEMBERSHIP_LEVELS
    ):
        abort(status.HTTP_400_BAD_REQUEST, description="Invalid membership level")

    target_level = target_level.lower()
    current_rank = MEMBERSHIP_LEVELS.index(customer.membership_level)
    target_rank = MEMBERSHIP_LEVELS.index(target_level)
    if target_rank < current_rank:
        abort(
            status.HTTP_409_CONFLICT,
            description="Cannot downgrade membership via upgrade action",
        )

    customer.membership_level = target_level
    customer.update()
    app.logger.info("Customer with id %s upgraded successfully", customer_id)
    return jsonify(customer.serialize()), status.HTTP_200_OK


# DOWNGRADE A CUSTOMER'S MEMBERSHIP
@app.route("/customers/<int:customer_id>/downgrade", methods=["PUT"])
def downgrade_customer(customer_id):
    """Downgrade a Customer's membership level"""
    app.logger.info("Request to downgrade customer with id: %s", customer_id)

    customer = Customer.find(customer_id)
    if not customer:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Customer with id '{customer_id}' was not found.",
        )

    data = request.get_json(silent=True)
    target_level = data.get("target_level") if isinstance(data, dict) else None
    if (
        not isinstance(target_level, str)
        or target_level.lower() not in MEMBERSHIP_LEVELS
    ):
        abort(status.HTTP_400_BAD_REQUEST, description="Invalid membership level")

    target_level = target_level.lower()
    current_rank = MEMBERSHIP_LEVELS.index(customer.membership_level)
    target_rank = MEMBERSHIP_LEVELS.index(target_level)
    if target_rank > current_rank:
        abort(
            status.HTTP_409_CONFLICT,
            description="Cannot upgrade membership via downgrade action",
        )

    customer.membership_level = target_level
    customer.update()
    app.logger.info("Customer with id %s downgraded successfully", customer_id)
    return jsonify(customer.serialize()), status.HTTP_200_OK
