Feature: The eCommerce customer service back-end
    As an eCommerce business administrator
    I need a RESTful customer service
    So that I can keep track of all my customers

Background:
    Given the customer service is running

Scenario: Create a Customer
    When I visit the "Customer Admin Portal" page
    And I set the "First Name" to "Emily"
    And I set the "Last Name" to "Chen"
    And I set the "Email" to "emily.chen@example.com"
    And I select "NY" in the "State" dropdown
    And I set the "City" to "New York"
    And I set the "Street" to "50 West 4th Street"
    And I set the "Postal Code" to "10012"
    And I press the "Create" button
    Then I should see a successful "created" message for customer "Emily Chen"
    When I press the "Clear" button
    Then the "First Name" field should be empty
    And the "Last Name" field should be empty
    And the "Email" field should be empty
    And the "State" field should be empty
    And the "City" field should be empty
    And the "Street" field should be empty
    And the "Postal Code" field should be empty
