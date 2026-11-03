"""Customer Service: update, upgrade and downgrade routes"""

from flask import current_app as app  # Import Flask application
from flask import jsonify, request, abort
from service.models import Customer, MEMBERSHIP_LEVELS
from service.common import status  # HTTP Status Codes


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
