"""Customer Service: create route"""

from flask import current_app as app
from flask import jsonify, request
from service.models import Customer
from service.common import status


# CREATE A NEW CUSTOMER
@app.route("/customers", methods=["POST"])
def create_customers():
    """Create a Customer"""
    app.logger.info("Request to Create a Customer...")
    data = request.get_json()
    customer = Customer()
    customer.deserialize(data)
    # Every new customer starts at bronze; the level can only be changed by upgrade/downgrade endpoints
    customer.membership_level = "bronze"
    customer.create()
    app.logger.info("Customer with new id [%s] created.", customer.id)
    location_url = f"{request.base_url}/{customer.id}"
    return (
        jsonify(customer.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )
