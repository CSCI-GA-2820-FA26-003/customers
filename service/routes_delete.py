"""Customer Service: delete route"""

from flask import current_app as app
from service.models import Customer
from service.common import status


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
