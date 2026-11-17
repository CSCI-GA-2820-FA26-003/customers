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


def _wait_for_alert(context: Any) -> str:
    """Return and accept the next browser alert."""
    alert = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.alert_is_present()
    )
    text = alert.text
    alert.accept()
    return text


@given("the customer service is running")
def run_customer_service(context: Any):
    """Check that the customer service is running"""
    context.driver.get(context.base_url)
    context.resp = requests.get(context.base_url + "/", timeout=context.wait_seconds)
    assert context.resp.status_code == 200


@given("the following customers")
def load_customers(context: Any):
    """Create the customers listed in the table."""
    rest_endpoint = f"{context.base_url}/customers"
    # save ids for read/update/delete tests
    # use email to retrieve the id of a customer in a later step
    context.customer_ids = {}
    context.customer_names = []
    for row in context.table:
        payload = {heading: row[heading] for heading in row.headings}
        response = requests.post(
            rest_endpoint, json=payload, timeout=context.wait_seconds
        )
        assert response.status_code == 201
        customer = response.json()
        context.customer_ids[payload["email"]] = customer["id"]
        context.customer_names.append(f"{payload['first_name']} {payload['last_name']}")
        # Upgrade the customer if a membership level is specified as not bronze
        membership_level = payload.get("membership_level", "bronze")
        if membership_level != "bronze":
            response = requests.put(
                f"{rest_endpoint}/{customer['id']}/upgrade",
                json={"target_level": membership_level},
                timeout=context.wait_seconds,
            )
            assert response.status_code == 200, response.text


@given('I visit the "Customer Admin Portal" page')
def visit_customer_admin_portal(context: Any):
    """Visit the Customer Admin Portal page"""
    context.driver.get(context.base_url)
    assert "Customer Admin Portal" in context.driver.title


@when('I click the "{tab_name}" tab')
def click_search_customer_tab(context: Any, tab_name: str):
    tab_ids = {
        "Create Customer": "create-tab",
        "Search Customer": "search-tab",
        "Manage Customer": "manage-tab",
    }
    tab_id = tab_ids.get(tab_name, tab_name)
    context.driver.find_element(By.ID, tab_id).click()


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
    assert _wait_for_alert(context) == (
        f"Customer {name} was successfully {action.lower()}!"
    )


@then('I should see the message "{message}"')
def verify_message(context: Any, message: str):
    """Verify the text of the browser alert"""
    alert = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.alert_is_present()
    )
    assert alert.text == message, f"Got alert: {alert.text}"
    alert.accept()


@then('I should see an error message containing "{message}"')
def verify_error_message(context: Any, message: str):
    """Verify the error message in the browser alert"""
    actual = _wait_for_alert(context)
    assert message in actual, f'Expected "{message}" in alert, got "{actual}"'


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


@then('I should see all customers in the "{element_name}" table')
def check_all_customers_in_table(context: Any, element_name: str):
    """Check that every fixture customer appears in a results table."""
    for customer_name in context.customer_names:
        check_text_in_table(context, customer_name, element_name)


@then('I should not see "{text}" in the "{element_name}" table')
def check_text_not_in_table(context: Any, text: str, element_name: str):
    """Check that text does not appear in a results table"""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    WebDriverWait(context.driver, context.wait_seconds).until(
        lambda d: text not in element.text
    )


@when("I enter the nonexistent customer's ID")
@when("I enter the existing customer's ID")
def enter_existing_customer_id(context):
    set_text_field(context, "ID", str(context.customer_id))


@when('I enter the customer ID for "{email}"')
def enter_customer_id_by_email(context: Any, email: str):
    """Look up a fixture customer by email and enter its ID."""
    customer_id = context.customer_ids[email]
    response = requests.get(
        f"{context.base_url}/customers/{customer_id}",
        timeout=context.wait_seconds,
    )
    assert response.status_code == 200, response.text
    customer = response.json()
    context.expected_customer = {
        field: value for field, value in customer.items() if field != "id"
    }
    set_text_field(context, "ID", str(customer_id))


@then("the form should show the existing customer's details")
def verify_customer_details(context):
    """Verify that the Read section displays the retrieved customer's details."""
    # The section is always in the DOM (just hidden), so wait for the AJAX
    # response to un-hide it instead of checking immediately.
    result = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.visibility_of_element_located((By.ID, "customer_result")),
        message="Customer details were not displayed",
    )

    for field, expected in context.expected_customer.items():
        actual = result.find_element(By.CSS_SELECTOR, f'[data-field="{field}"]').text
        assert actual == expected, f"{field}: expected {expected!r}, got {actual!r}"


@given("a customer ID that does not exist")
def prepare_nonexistent_customer_id(context):
    """Create and delete a test customer so its ID is known to be absent."""
    customer = {
        "first_name": "invalid",
        "last_name": "customer",
        "email": "invalid.customer@example.com",
        "street": "123 Main St",
        "city": "Anytown",
        "state": "NY",
        "postal_code": "00000",
    }
    response = requests.post(
        f"{context.base_url}/customers",
        json=customer,
        timeout=context.wait_seconds,
    )
    assert response.status_code == 201, response.text
    context.customer_id = response.json()["id"]
    context.expected_customer = {**customer, "membership_level": "bronze"}
    response = requests.delete(
        f"{context.base_url}/customers/{context.customer_id}",
        timeout=10,
    )
    assert response.status_code == 204, response.text


@then('the "{element_name}" field should contain "{text_string}"')
def check_field_value(context: Any, element_name: str, text_string: str):
    """Check that a field or dropdown holds the expected value"""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.visibility_of_element_located((By.ID, element_id))
    )
    actual = element.get_attribute("value")
    assert (
        actual == text_string
    ), f"{element_id}: expected {text_string!r}, got {actual!r}"


@then('the "{button}" button should be disabled')
def check_button_disabled(context: Any, button: str):
    """Check that a button is disabled"""
    button_id = ID_PREFIX + button.lower().replace(" ", "_") + "-btn"
    element = context.driver.find_element(By.ID, button_id)
    WebDriverWait(context.driver, context.wait_seconds).until(
        lambda d: not element.is_enabled()
    )


@when('I open "{name}" from the search results')
def open_customer_from_search(context: Any, name: str):
    """Search by the customer's last name and open them in Manage Customer"""
    last_name = name.split()[-1]
    click_search_customer_tab(context, "Search Customer")
    set_text_field(context, "Query Last Name", last_name)
    press_button(context, "Search")
    _click_row_in_table(context, name, "Search Results")


@when('the customer "{email}" is deleted')
def delete_customer_by_email(context: Any, email: str):
    """Delete a fixture customer through the API, behind the UI's back"""
    customer_id = context.customer_ids[email]
    response = requests.delete(
        f"{context.base_url}/customers/{customer_id}",
        timeout=context.wait_seconds,
    )
    assert response.status_code == 204, response.text


@when('the customer "{email}" is upgraded to "{level}"')
def upgrade_customer_by_email(context: Any, email: str, level: str):
    """Upgrade a fixture customer through the API, behind the UI's back"""
    customer_id = context.customer_ids[email]
    response = requests.put(
        f"{context.base_url}/customers/{customer_id}/upgrade",
        json={"target_level": level},
        timeout=context.wait_seconds,
    )
    assert response.status_code == 200, response.text


def _click_row_in_table(context: Any, text: str, element_name: str):
    """Click the first table row that contains the given text"""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    check_text_in_table(context, text, element_name)
    rows = context.driver.find_elements(By.CSS_SELECTOR, f"#{element_id} tbody tr")
    row = next(r for r in rows if text in r.text)
    row.click()
