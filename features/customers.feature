Feature: The eCommerce customer service back-end
    As an eCommerce business administrator
    I need a RESTful customer service
    So that I can keep track of all my customers

Background:
    Given the customer service is running
    And the following customers
        | first_name | last_name | email                     | street             | city     | state | postal_code | membership_level |
        | Emily      | Chen      | emily.chen@example.com    | 50 West 4th Street | New York | NY    | 10012       | bronze           |
        | Alex       | Chen      | alex.chen@example.com     | 75 Madison Avenue  | Albany   | NY    | 12210       | silver           |
        | Grace      | Lee       | grace.lee@example.com     | 10 Park Avenue     | Buffalo  | NY    | 14201       | silver           |
        | Michael    | Brown     | michael.brown@example.com | 100 Main Street    | Albany   | NY    | 12207       | gold             |
        | Sophia     | Davis     | sophia.davis@example.com  | 200 Oak Avenue     | Boston   | MA    | 02108       | bronze           |
        | Priya      | Patel     | priya.patel@example.com   | 200 Clarendon St   | Boston   | MA    | 02116       | gold             |
    And I visit the "Customer Admin Portal" page

# Create Customer
Scenario: Create a Customer
    When I set the "First Name" to "Ada"
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
    And the "State" dropdown should be unset
    And the "City" field should be empty
    And the "Street" field should be empty
    And the "Postal Code" field should be empty

Scenario: Create a Customer with an email that is already used
    When I set the "First Name" to "Nora"
    And I set the "Last Name" to "Lee"
    And I set the "Email" to "priya.patel@example.com"
    And I select "MA" in the "State" dropdown
    And I set the "City" to "Cambridge"
    And I set the "Street" to "77 Massachusetts Avenue"
    And I set the "Postal Code" to "02139"
    And I press the "Create" button
    Then I should see an error message containing "Customer with email 'priya.patel@example.com' already exists."

# List Customers
Scenario: List all Customers
    When I click the "Search Customer" tab
    And I press the "Search" button
    Then I should see all customers in the "Search Results" table

# Query Customers
Scenario: Query customers by last name
    When I click the "Search Customer" tab
    And I set the "Query Last Name" to "Chen"
    And I press the "Search" button
    Then I should see "Emily Chen" in the "Search Results" table
    And I should see "Alex Chen" in the "Search Results" table

Scenario: Query customers by multiple fields returns the intersection
    When I click the "Search Customer" tab
    And I select "NY" in the "Query State" dropdown
    And I select "Silver" in the "Query Membership Level" dropdown
    And I press the "Search" button
    Then I should see "Alex Chen" in the "Search Results" table
    And I should see "Grace Lee" in the "Search Results" table
    And I should not see "Emily Chen" in the "Search Results" table
    And I should not see "Michael Brown" in the "Search Results" table
    And I should not see "Daniel Wilson" in the "Search Results" table
    And I should not see "Sophia Davis" in the "Search Results" table
    And I should not see "Priya Patel" in the "Search Results" table

Scenario: Query customers with no matching results
    When I click the "Search Customer" tab
    And I set the "Query Last Name" to "Nomatch"
    And I press the "Search" button
    Then I should see an error message containing "Customer does not exist with the given search criteria."
    And I should not see "Nomatch" in the "Search Results" table

# Read a Customer
Scenario: Retrieve an existing customer by ID
    When I click the "Search Customer" tab
    And I enter the customer ID for "emily.chen@example.com"
    And I press the "Retrieve" button
    Then the form should show the existing customer's details

Scenario: Retrieve a customer that does not exist
    Given a customer ID that does not exist
    When I click the "Search Customer" tab
    And I enter the nonexistent customer's ID
    And I press the "Retrieve" button
    Then I should see an error message containing "not found"

# Upgrade a Customer
Scenario: Upgrade a customer's membership level
    When I open "Sophia Davis" from the search results
    Then the "Manage Membership Level" field should contain "bronze"
    When I select "Gold" in the "Upgrade Level" dropdown
    And I press the "Upgrade" button
    Then I should see a successful "upgraded" message for customer "Sophia Davis"
    And the "Manage Membership Level" field should contain "gold"
    And the "Upgrade" button should be disabled
    
Scenario: Upgrade a customer that does not exist
    When I open "Sophia Davis" from the search results
    And the customer "sophia.davis@example.com" is deleted
    And I select "Gold" in the "Upgrade Level" dropdown
    And I press the "Upgrade" button
    Then I should see an error message containing "not found"

Scenario: Upgrade a customer to a lower level than their current one
    When I open "Sophia Davis" from the search results
    And the customer "sophia.davis@example.com" is upgraded to "gold"
    And I select "Silver" in the "Upgrade Level" dropdown
    And I press the "Upgrade" button
    Then I should see an error message containing "Cannot downgrade membership via upgrade action"
