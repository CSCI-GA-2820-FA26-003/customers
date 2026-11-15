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
    """Delete all customers, then create the ones listed in the table"""
    rest_endpoint = f"{context.base_url}/customers"
    response = requests.get(rest_endpoint, timeout=context.wait_seconds)
    assert response.status_code == 200
    for customer in response.json():
        response = requests.delete(
            f"{rest_endpoint}/{customer['id']}", timeout=context.wait_seconds
        )
        assert response.status_code == 204
    for row in context.table:
        payload = {heading: row[heading] for heading in row.headings}
        response = requests.post(
            rest_endpoint, json=payload, timeout=context.wait_seconds
        )
        assert response.status_code == 201


@when('I visit the "Customer Admin Portal" page')
def visit_customer_admin_portal(context: Any):
    """Visit the Customer Admin Portal page"""
    context.driver.get(context.base_url)
    assert "Customer Admin Portal" in context.driver.title


@when('I click the "Search Customer" tab')
def click_search_customer_tab(context):
    context.driver.find_element(By.ID, "search-tab").click()


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


@then('I should see "{text}" in the "{element_name}" table')
def check_text_in_table(context: Any, text: str, element_name: str):
    """Check that text appears in a results table"""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    WebDriverWait(context.driver, context.wait_seconds).until(
        lambda d: text in element.text
    )


@when('I create a customer "{first_name}" "{last_name}" in "{city}", ' '"{state}"')
def create_customer(context: Any, **fields: str):
    """Create a customer through the Create form"""
    values = {
        "first_name": fields["first_name"],
        "last_name": fields["last_name"],
        "city": fields["city"],
        "email": f"{fields['first_name']}.{fields['last_name']}@example.com".lower(),
        "street": "1 Main Street",
        "postal_code": "10001",
    }
    for key, value in values.items():
        element = context.driver.find_element(By.ID, ID_PREFIX + key)
        element.clear()
        element.send_keys(value)
    state = Select(context.driver.find_element(By.ID, ID_PREFIX + "state"))
    state.select_by_visible_text(fields["state"])
    context.driver.find_element(By.ID, "customer_create-btn").click()
    alert = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.alert_is_present()
    )
    alert.accept()


@then('I should not see "{text}" in the "{element_name}" table')
def check_text_not_in_table(context: Any, text: str, element_name: str):
    """Check that text does not appear in a results table"""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    WebDriverWait(context.driver, context.wait_seconds).until(
        lambda d: text not in element.text
    )
@given("a customer with bronze membership exists")
def create_bronze_customer(context):
    """Create a customer and remember the details for the Retrieve test."""
    customer = {
        "first_name": "Emily",
        "last_name": "Chen",
        "email": "emilychen@example.com",
        "street": "50 West 4th Street",
        "city": "New York",
        "state": "NY",
        "postal_code": "10012",
    }
    response = requests.post(f"{context.base_url}/customers", json=customer, timeout=10)
    assert response.status_code == 201, response.text
    context.customer_id = response.json()["id"]
    context.expected_customer = {**customer, "membership_level": "bronze"}


@when("I enter the nonexistent customer's ID")
@when("I enter the existing customer's ID")
def enter_existing_customer_id(context):
    set_text_field(context, "ID", str(context.customer_id))


@then('I should see an alert saying "{message}"')
def verify_alert_message(context, message):
    alert = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.alert_is_present()
    )
    assert alert.text == message
    alert.accept()


@then("the form should show the existing customer's details")
def verify_customer_details(context):
    """Verify that the Read section displays the retrieved customer's details."""
    result = context.driver.find_element(By.ID, "customer_result")
    assert result.is_displayed()

    for field, expected in context.expected_customer.items():
        actual = result.find_element(By.CSS_SELECTOR, f'[data-field="{field}"]').text
        assert actual == expected, f"{field}: expected {expected!r}, got {actual!r}"


@given("a customer ID that does not exist")
def prepare_nonexistent_customer_id(context):
    """Create and delete a test customer so its ID is known to be absent."""
    create_bronze_customer(context)
    response = requests.delete(
        f"{context.base_url}/customers/{context.customer_id}",
        timeout=10,
    )
    assert response.status_code == 204, response.text


@then('I should see an alert containing "{message}"')
def verify_alert_contains(context, message):
    """Check that the alert contains the expected text."""
    alert = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.alert_is_present()
    )
    actual = alert.text
    alert.accept()
    assert message in actual, f"Expected {message!r} in alert, got {actual!r}"
