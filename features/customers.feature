Feature: The eCommerce customer service back-end
    As an eCommerce business administrator
    I need a RESTful customer service
    So that I can keep track of all my customers

Background:
    Given the customer service is running
        And the following customers
        | first_name | last_name | email                  | street             | city     | state | postal_code |
        | Emily      | Chen      | emily.chen@example.com | 50 West 4th Street | New York | NY    | 10012       |

Scenario: Create a Customer
    When I visit the "Customer Admin Portal" page
    And I set the "First Name" to "Ada"
    And I set the "Last Name" to "Wang"
    And I set the "Email" to "ada.wang@example.com"
    And I select "NY" in the "State" dropdown
    And I set the "City" to "New York"
    And I set the "Street" to "50 West 4th Street"
    And I set the "Postal Code" to "10012"
    And I press the "Create" button
    Then I should see a successful "created" message for customer "Ada Wang"
    When I press the "Clear" button
    Then the "First Name" field should be empty
    And the "Last Name" field should be empty
    And the "Email" field should be empty
    And the "State" field should be empty
    And the "City" field should be empty
    And the "Street" field should be empty
    And the "Postal Code" field should be empty

Scenario: List all Customers
    When I visit the "Customer Admin Portal" page
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
    
Scenario: Create a Customer with an email that is already used
    Given the following customers
        | first_name | last_name | email                   | street           | city   | state | postal_code |
        | Priya      | Patel     | priya.patel@example.com | 200 Clarendon St | Boston | MA    | 02116       |
    When I visit the "Customer Admin Portal" page
    And I set the "First Name" to "Nora"
    And I set the "Last Name" to "Lee"
    And I set the "Email" to "priya.patel@example.com"
    And I select "MA" in the "State" dropdown
    And I set the "City" to "Cambridge"
    And I set the "Street" to "77 Massachusetts Avenue"
    And I set the "Postal Code" to "02139"
    And I press the "Create" button
    Then I should see an error message containing "Customer with email 'priya.patel@example.com' already exists."

Scenario: Retrieve an existing customer by ID
    Given a customer with bronze membership exists
    When I visit the "Customer Admin Portal" page
    And I click the "Search Customer" tab
    And I enter the existing customer's ID
    And I press the "Retrieve" button
    Then I should see an alert saying "Success"
    And the form should show the existing customer's details

Scenario: Retrieve a customer that does not exist
    Given a customer ID that does not exist
    When I visit the "Customer Admin Portal" page
    And I click the "Search Customer" tab
    And I enter the nonexistent customer's ID
    And I press the "Retrieve" button
    Then I should see an alert containing "not found"

