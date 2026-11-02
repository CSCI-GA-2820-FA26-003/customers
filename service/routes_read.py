"""Customer Service: read and list routes"""

from flask import current_app as app  # Import Flask application
from flask import jsonify, abort
from service.models import Customer
from service.common import status  # HTTP Status Codes


# Read a Customer
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
