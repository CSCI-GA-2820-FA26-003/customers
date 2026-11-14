##################################################################
# This code works because of the following naming convention:
#
# 1. UI element ID begins with "customer_" and follows snake_case
#  naming convention. For example, the "Postal Code" field has an id of
# 'customer_postal_code'.
#
# 2. The buttons have an id followed by '-btn', so the "Clear" button has
#  an id of 'customer_clear-btn'.
#
# 3. The forms have an id followed by '-form', so the "Create Customer"
# form has an id of 'customer_create-form'.
##################################################################

# import re
import requests

# import logging
from typing import Any
from behave import given, when, then  # pylint: disable=no-name-in-module
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions

ID_PREFIX = "customer_"


@given("the customer service is running")
def run_customer_service(context: Any):
    """Check that the customer service is running"""
    context.driver.get(context.base_url)
    context.resp = requests.get(context.base_url + "/", timeout=context.wait_seconds)
    assert context.resp.status_code == 200


@given("the following customers")
def load_customers(context: Any):
    """Create the customers in the table through the REST API"""
    for row in context.table:
        customer = {heading: row[heading] for heading in row.headings}
        resp = requests.post(
            f"{context.base_url}/customers", json=customer, timeout=context.wait_seconds
        )
        assert (
            resp.status_code == 201
        ), f"Could not create {customer['email']}: {resp.text}"


@when('I visit the "Customer Admin Portal" page')
def visit_customer_admin_portal(context: Any):
    """Visit the Customer Admin Portal page"""
    context.driver.get(context.base_url)
    assert "Customer Admin Portal" in context.driver.title


@when('I set the "{element_name}" to "{text_string}"')
def set_text_field(context: Any, element_name: str, text_string: str):
    """Set the value of a text field"""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(text_string)


@when('I select "{text_string}" in the "{element_name}" dropdown')
def select_in_dropdown(context: Any, text_string: str, element_name: str):
    """Select a value from a dropdown"""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    select_element = Select(context.driver.find_element(By.ID, element_id))
    select_element.select_by_visible_text(text_string)


@when('I press the "{button}" button')
def press_button(context: Any, button: str):
    """Press a button on the page"""
    button_id = ID_PREFIX + button.lower().replace(" ", "_") + "-btn"
    button_element = context.driver.find_element(By.ID, button_id)
    button_element.click()


@then('I should see a successful "{action}" message for customer "{name}"')
def verify_success_message_for(context: Any, name: str, action: str):
    """Verify the success message in the browser alert"""
    alert = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.alert_is_present()
    )

    assert alert.text == f"Customer {name} was successfully {action.lower()}!"
    alert.accept()


@then('I should see an error message containing "{message}"')
def verify_error_message(context: Any, message: str):
    """Verify the error message in the browser alert"""
    alert = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.alert_is_present()
    )
    text = alert.text
    alert.accept()
    assert message in text, f'Expected "{message}" in alert, got "{text}"'


@then('the "{element_name}" field should be empty')
def check_field_empty(context: Any, element_name: str):
    """Check that a field is empty"""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    assert element.get_attribute("value") == ""


@then('the "{element_name}" dropdown should be unset')
def check_dropdown_unset(context: Any, element_name: str):
    """Check that a dropdown is unset"""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    select_element = Select(context.driver.find_element(By.ID, element_id))
    selected_option = select_element.first_selected_option
    assert selected_option.text == ""
