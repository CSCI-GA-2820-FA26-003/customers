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

from flask import jsonify, abort, url_for
from flask import current_app as app  # Import Flask application

from service.models import Customer
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


# list all customers
@app.route("/customers", methods=["GET"])
def list_customers():
    """List All Customers"""
    app.logger.info("Request to list all customers")
    customers = Customer.all()

    results = [customer.serialize() for customer in customers]
    app.logger.info("Returning %d customers", len(results))
    return jsonify(results), status.HTTP_200_OK


from service import routes_create  # noqa: F401,E402 # pylint: disable=all
from service import routes_update  # noqa: F401,E402 # pylint: disable=all
from service import routes_delete  # noqa: F401,E402 # pylint: disable=all
