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

Scenario: List all Customers
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
    And I press the "Search" button
    Then I should see "Emily" in the "Search Results" table

Scenario: Query customers by last name
    When I visit the "Customer Admin Portal" page
    And I create a customer "Alice" "Harbor" in "New York", "NY"
    And I create a customer "Bob" "Quartz" in "Albany", "NY"
    And I press the "Clear" button
    And I set the "Last Name" to "Harbor"
    And I press the "Search" button
    Then I should see "Alice" in the "Search Results" table
    And I should not see "Bob" in the "Search Results" table

Scenario: Query customers by multiple fields returns the intersection
    When I visit the "Customer Admin Portal" page
    And I create a customer "Alice" "Cedar" in "New York", "NY"
    And I create a customer "Bob" "Cedar" in "Oakland", "CA"
    And I press the "Clear" button
    And I set the "Last Name" to "Cedar"
    And I select "NY" in the "State" dropdown
    And I select "Bronze" in the "Membership Level" dropdown
    And I press the "Search" button
    Then I should see "Alice" in the "Search Results" table
    And I should not see "Bob" in the "Search Results" table

Scenario: Query customers with no matching results
    When I visit the "Customer Admin Portal" page
    And I create a customer "Alice" "Zephyr" in "New York", "NY"
    And I press the "Clear" button
    And I press the "Search" button
    Then I should see "Alice" in the "Search Results" table
    When I set the "Last Name" to "Nomatch"
    And I press the "Search" button
    Then I should not see "Alice" in the "Search Results" table