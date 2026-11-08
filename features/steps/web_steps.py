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


@given('the customer service is running')
def run_customer_service(context: Any):
    """Check if the customer service is running"""
    context.driver.get(context.base_url)
    context.resp = requests.get(context.base_url + '/')
    assert context.resp.status_code == 200


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


@when('I set the "Name" to "Emily Chen"')
def set_name_to_emily_chen(context: Any):
    """Set the Name field to 'Emily Chen'"""
    set_text_field(context, "Name", "Emily Chen")


@when('I select "{text_string}" in the "{element_name}" dropdown')
def select_in_dropdown(context: Any, text_string: str, element_name: str):
    """Select a value from a dropdown"""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    select_element = Select(context.driver.find_element(By.ID, element_id))
    select_element.select_by_visible_text(text_string)


@when('I select "NY" in the "State" dropdown')
def select_ny_in_state_dropdown(context: Any):
    """Select 'NY' in the 'State' dropdown"""
    select_in_dropdown(context, "NY", "State")


@when('I set the "City" to "New York"')
def set_city_to_new_york(context: Any):
    """Set the City field to 'New York'"""
    set_text_field(context, "City", "New York")


@when('I set the "Street" to "50 West 4th Street"')
def set_street_to_50_west_4th_street(context: Any):
    """Set the Street field to '50 West 4th Street'"""
    set_text_field(context, "Street", "50 West 4th Street")


@when('I set the "Postal Code" to "10012"')
def set_postal_code_to_10012(context: Any):
    """Set the Postal Code field to '10012'"""
    set_text_field(context, "Postal Code", "10012")


@when('I press the "{button}" button')
def press_button(context: Any, button: str):
    """Press a button on the page"""
    button_id = ID_PREFIX + button.lower().replace(" ", "_") + "-btn"
    button_element = context.driver.find_element(By.ID, button_id)
    button_element.click()


@when('I press the "Create" button')
def press_create_button(context: Any):
    """Press the 'Create' button"""
    press_button(context, "Create")


@then('I should see a successful “{action}” message for customer "{name}"')
def verify_success_message_for(context: Any, name: str, action: str):
    """Verify the success message in the browser alert"""
    alert = WebDriverWait(
        context.driver, context.wait_seconds
    ).until(expected_conditions.alert_is_present())

    assert alert.text == f"Customer {name} was successfully {action.lower()}!"
    alert.accept()


@then('I should see a success message for customer "Emily Chen"')
def verify_success_message_for_emily_chen(context: Any):
    """Verify the text in the browser alert for customer 'Emily Chen'"""
    verify_success_message_for(context, "Emily Chen", "created")


@when('I press the "Clear" button')
def press_clear_button(context: Any):
    """Press the 'Clear' button"""
    press_button(context, "Clear")


@then('the "{element_name}" field should be empty')
def check_field_empty(context: Any, element_name: str):
    """Check that a field is empty"""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    assert element.get_attribute("value") == ""


@then('the "Name" field should be empty')
def check_name_field_empty(context):
    """Check that Name field is empty"""
    check_field_empty(context, "Name")

@then('the "{element_name}" dropdown should be unset')
def check_dropdown_unset(context: Any, element_name: str):
    """Check that a dropdown is unset"""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    select_element = Select(context.driver.find_element(By.ID, element_id))
    selected_option = select_element.first_selected_option
    assert selected_option.text == ""


@then('the "State" dropdown should be unset')
def check_state_dropdown_unset(context):
    """Check that State dropdown is unset"""
    check_dropdown_unset(context, "State")


@then('the "City" field should be empty')
def check_city_field_empty(context):
    """Check that City field is empty"""
    check_field_empty(context, "City")


@then(u'the "Street" field should be empty')
def check_street_field_empty(context):
    """Check that Street field is empty"""
    check_field_empty(context, "Street")


@then('the "Postal Code" field should be empty')
def check_postal_code_field_empty(context):
    """Check that Postal Code field is empty"""
    check_field_empty(context, "Postal Code")
