"""Customer Service: read and list routes"""

from flask import current_app as app  # Import Flask application
from flask import jsonify, abort, request
from service.models import (
    Customer,
    DataValidationError,
    MEMBERSHIP_LEVELS,
    POSTAL_CODE_PATTERN,
    US_STATE_CODES,
)
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


# LIST ALL CUSTOMERS
@app.route("/customers", methods=["GET"])
def list_customers():
    """List customers matching all supplied filters."""
    app.logger.info("Request to list customers")
    filters = customer_query_filters()
    customers = Customer.find_by_filters(filters)

    results = [customer.serialize() for customer in customers]
    app.logger.info("Returning %d customers", len(results))
    return jsonify(results), status.HTTP_200_OK


# Extract and validate customer query filters
def customer_query_filters():
    """Extract and validate customer query parameters."""
    filters = {}

    for field in (
        "membership_level",
        "state",
        "city",
        "postal_code",
        "last_name",
        "first_name",
    ):
        if field in request.args:
            value = request.args[field]
            if not value.strip():
                raise DataValidationError(f"Invalid query: {field} must not be blank")
            filters[field] = value

    if "city" in filters and "state" not in filters:
        raise DataValidationError(
            "Invalid query: state is required when filtering by city"
        )

    if "state" in filters:
        filters["state"] = filters["state"].upper()

    validators = {
        "state": US_STATE_CODES.__contains__,
        "membership_level": MEMBERSHIP_LEVELS.__contains__,
        "postal_code": POSTAL_CODE_PATTERN.fullmatch,
    }

    for field, validate in validators.items():
        if field in filters and not validate(filters[field]):
            raise DataValidationError(f"Invalid query: invalid {field}")

    return filters
