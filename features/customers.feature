Feature: The eCommerce customer service back-end
    As an eCommerce business administrator
    I need a RESTful customer service
    So that I can keep track of all my customers

BackGround:
    Given the customer service is running

Scenario: Create a Customer
    When I visit the "Customer Admin Portal" page
    And I set the "First Name" to "Emily"
    And I set the "Last Name" to "Chen"
    And I select "NY" in the "State" dropdown
    And I set the "City" to "New York"
    And I set the "Street" to "50 West 4th Street"
    And I set the "Postal Code" to "10012"
    And I press the "Create" button
    Then I should see a successful "created" message for customer "Emily Chen"
    When I press the "Clear" button
    Then the "First Name" field should be empty
    And the "Last Name" field should be empty
    And the "State" field should be empty
    And the "City" field should be empty
    And the "Street" field should be empty
    And the "Postal Code" field should be empty

Scenario: Retrieve an existing customer by ID
    Given a customer with bronze membership exists
    When I visit the "Customer Admin Portal" page
    And I enter the existing customer's ID
    And I press the "Retrieve" button
    Then I should see an alert saying "Success"
    And the form should show the existing customer's details

Scenario: Retrieve a customer that does not exist
    Given a customer ID that does not exist
    When I visit the "Customer Admin Portal" page
    And I enter the nonexistent customer's ID
    And I press the "Retrieve" button
    Then I should see an alert containing "not found"