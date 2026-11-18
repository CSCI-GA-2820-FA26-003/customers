# NYU DevOps Project Customer Service

[![CI](https://github.com/CSCI-GA-2820-FA26-003/customers/actions/workflows/ci.yaml/badge.svg?branch=master)](https://github.com/CSCI-GA-2820-FA26-003/customers/actions/workflows/ci.yaml)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-FA26-003/customers/branch/master/graph/badge.svg)](https://app.codecov.io/gh/CSCI-GA-2820-FA26-003/customers/tree/master)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

## Overview

The **Customer** service manages customer records for DevOps E-commerce project. The client uses its REST API to perform operations such as creating customers, querying customers by ID, updating customer details, and deleting customers.

## Get Started

### Prerequisites

The following software is required to run this repository:

* [Docker](https://www.docker.com/products/docker-desktop/)

* [Microsoft VS Code](https://code.visualstudio.com/Download)

### Clone the Repo

These should be copied using a bash shell as follows:

```bash
git clone https://github.com/CSCI-GA-2820-FA26-003/customers.git

cd ~/customers

code .
```

### Run the Service

Start the service in the development container:

```bash
honcho start
```

The API is available at http://localhost:8080. Request and response bodies use JSON. Requests with a JSON body must include the `Content-Type: application/json` header.

### Deploy with Kubernetes

Run the following commands from the repository root in the development
container. If `honcho` is running on port `8080`, stop it before creating
the cluster so the k3d load balancer can use that port.

```bash
make cluster
make build
make push
make deploy
```

These commands create a local k3d cluster and registry, build and push
the customer service image, and apply the Kubernetes manifests.

Wait for the customer service deployment to roll out:

```bash
kubectl rollout status deployment/customers
```

Verify that the service responds through the Ingress:

```bash
curl -i http://localhost:8080/health
```

Expect `200 OK` and a JSON response of `{"status":"OK"}`.

The PostgreSQL Secret is included in `k8s/postgres/secret.yaml`. It can also
be created manually with:

```bash
kubectl create secret generic postgres-secret \
  --from-literal=username=postgres \
  --from-literal=password=pgs3cr3t \
```
These credentials are for coursework only; do not
commit real production credentials. Inject production credentials through a
secret manager instead.

### Use the Customer Admin Portal

With the service running, open `http://localhost:8080/` in your browser.

1. In **Create Customer**, fill in the required fields and click **Create**.
   Open **Search Customer** and note the ID in the **Customer ID** field.
2. In **Search Customer**, enter a customer ID and click **Retrieve** to view
   that customer's details. To list all customers, leave **Search by Filters**
   blank and click **Search**. To narrow the list, use **City**, **State**,
   **Last Name**, or **Membership Level**. Select a **State** whenever you enter
   a **City**.
3. Click a row in **Search Results** to open the customer in **Manage Customer**.
   Edit the customer's details and click **Update**, or select a target level
   under **Upgrade Membership** or **Downgrade Membership** and click the
   corresponding button. To remove the customer, check the prefilled ID under
   **Delete Customer** and click **Delete**.

## Database Structure

The current database structure is as follows. Only US addresses are supported.

> **Schema change:** the single `address` column was replaced by `street`, `city`, `state` and `postal_code`, and a `membership_level` column was added. Existing data is not migrated: run `flask db-create` to drop and recreate the tables.

> **Email upgrade:** the `email` column is added to existing databases automatically when the service starts, without losing data. See [Email Column Upgrade](#email-column-upgrade).

| Field | Type |  Description |
|-------|------|-------------|
| `id` | Integer | Primary key, used as `{customer_id}` in URLs. |
| `first_name` | String, up to 63 characters | Customer first name. Cannot be null, empty, or whitespace-only. |
| `last_name` | String, up to 63 characters | Customer last name. Cannot be null, empty, or whitespace-only. |
| `email` | String, up to 255 characters | Customer email in `local@domain.tld` format, e.g. `devops@example.com`. Required and unique: no two customers can share an email. Cannot be null, empty, or whitespace-only. |
| `street` | String, up to 255 characters | Street address. Cannot be null, empty, or whitespace-only. |
| `city` | String, up to 63 characters | City. Cannot be null, empty, or whitespace-only. |
| `state` | String, 2 characters | US state code, e.g. `NY`. Must be a USPS code (50 states, DC, territories or Freely Associated States); lowercase input is stored uppercase. |
| `postal_code` | String, up to 10 characters | US ZIP code in `12345` or `12345-6789` format. |
| `membership_level` | String | One of `bronze`, `silver`, or `gold`. Defaults to `bronze`. |

Example customer representation:

```json
{
  "id": 1,
  "first_name": "DevOps",
  "last_name": "Team",
  "email": "devops@example.com",
  "street": "251 Mercer St",
  "city": "New York",
  "state": "NY",
  "postal_code": "10012",
  "membership_level": "bronze"
}
```

### Email Column Upgrade

`db.create_all()` only creates missing tables and never changes an existing one, so a database created before the `email` column was added would keep its old `customers` table and every customer request would fail with `column customers.email does not exist`. To prevent this, the service upgrades the schema itself on every startup, right after `db.create_all()` (`service/common/db_upgrade.py`):

1. **Check:** if `customers.email` already exists, is `NOT NULL`, and has the `customers_email_key` (unique) and `customers_email_not_blank` constraints, the schema is current and nothing is changed. This is the case for new databases and on every startup after the first upgrade.
2. **Upgrade:** otherwise the service adds the `email` column, backfills existing customers, then sets `NOT NULL` and adds both constraints, using the same names `db.create_all()` gives them on a new database.

Things to know:

* **Existing data is kept.** Each customer that existed before the upgrade gets a unique placeholder email `customer-<id>@example.invalid` (`.invalid` is a reserved domain, so it can never be a real address), and a warning with the number of customers is logged. Replace placeholders with real addresses through `PUT /customers/{customer_id}`; they can be found with `GET /customers` or by searching the database for `@example.invalid`.

## APIs

Examples use `http://localhost:8080`.

### Open the Customer Admin Portal

`GET /` serves the Customer Admin Portal. Open `http://localhost:8080/` in your browser.

### Check service health

`GET /health` returns `200 OK` with a JSON status. To check the running service, run:

```bash
curl -i http://localhost:8080/health
```

The response body is:

```json
{"status":"OK"}
```

### Create a Customer

`POST /customers`

```bash
curl -i -X POST http://localhost:8080/customers \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "DevOps",
    "last_name": "Team",
    "email": "devops@example.com",
    "street": "251 Mercer St",
    "city": "New York",
    "state": "NY",
    "postal_code": "10012"
  }'
```

`email` is required and must not already belong to another customer. Every new customer is created with the `bronze` membership level. `membership_level` is not needed in the request; if a valid level is given, it is ignored. Use [Update a Customer](#update-a-customer) to change the level.

Example response for a newly assigned ID of `1`:

```http
HTTP/1.1 201 CREATED
Content-Type: application/json
Location: http://localhost:8080/customers/1

{
  "id": 1,
  "first_name": "DevOps",
  "last_name": "Team",
  "email": "devops@example.com",
  "street": "251 Mercer St",
  "city": "New York",
  "state": "NY",
  "postal_code": "10012",
  "membership_level": "bronze"
}
```

| Result | Status |
|--------|--------|
| Customer created | `201` |
| Missing required field, invalid email, malformed JSON, or database constraint violation | `400` |
| Email already used by another customer | `409` |
| Missing or unsupported JSON content type | `415` |

### Read a Customer

`GET /customers/{customer_id}`

```bash
curl -i http://localhost:8080/customers/1
```

Returns the customer representation shown above with `200 OK`. If no customer exists for the requested ID, the response is `404 Not Found`.

### Update a Customer

`PUT /customers/{customer_id}`

```bash
curl -i -X PUT http://localhost:8080/customers/1 \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Customer",
    "last_name": "Squad",
    "email": "customer.squad@example.com",
    "street": "44 W Fourth St",
    "city": "New York",
    "state": "NY",
    "postal_code": "10003",
    "membership_level": "gold"
  }'
```

Provide all name, email and address fields, including both `first_name` and `last_name`, including any value you want to keep. The email can be changed, but not to one that belongs to another customer; keeping the customer's own email is allowed. `membership_level` is optional; if it is omitted, the current level is kept. Partial updates and `PATCH` requests are not implemented.

Example response body with `200 OK`:

```json
{
  "id": 1,
  "first_name": "Customer",
  "last_name": "Squad",
  "email": "customer.squad@example.com",
  "street": "44 W Fourth St",
  "city": "New York",
  "state": "NY",
  "postal_code": "10003",
  "membership_level": "gold"
}
```

| Result | Status |
|--------|--------|
| Customer updated | `200` |
| Customer does not exist | `404` |
| Missing required field, invalid email, malformed JSON, or database constraint violation | `400` |
| Email already used by another customer | `409` |

The route checks whether the customer exists before reading the body, so a request for a missing customer returns `404` before body validation.

### Delete a Customer

`DELETE /customers/{customer_id}`

```bash
curl -i -X DELETE http://localhost:8080/customers/1
```

Returns `204 No Content` with an empty body. Deleting an ID that does not exist also returns `204`, making repeated delete requests idempotent.

### List and Query Customers

`GET /customers` lists all customers when you omit query parameters.

```bash
curl -i http://localhost:8080/customers
```

To filter the results, use `first_name`, `last_name`, `email`, `city`,
`state`, `postal_code`, or `membership_level`. When you supply multiple
filters, each customer must match all of them. Include `state` whenever
you filter by `city`.

```bash
curl -i --get http://localhost:8080/customers \
  --data-urlencode "city=New York" \
  --data-urlencode "state=NY" \
  --data-urlencode "membership_level=bronze"
```

The service returns `200 OK` with a JSON array. If no customers match,
the response body is `[]`.

```json
[
  {
    "id": 1,
    "first_name": "DevOps",
    "last_name": "Team",
    "email": "devops@example.com",
    "street": "251 Mercer St",
    "city": "New York",
    "state": "NY",
    "postal_code": "10012",
    "membership_level": "bronze"
  }
]
```

The service returns `400 Bad Request` if you supply `city` without `state`,
leave a supported filter blank, or supply an invalid `state`,
`membership_level`, `postal_code`, or `email`. The following request
returns `400 Bad Request` because it omits `state`.

```bash
curl -i --get http://localhost:8080/customers \
  --data-urlencode "city=New York"
```

### Upgrade or Downgrade Customer Membership

Use `PUT /customers/{id}/upgrade` to move to a higher membership level
and `PUT /customers/{id}/downgrade` to move to a lower level. Both
endpoints accept a JSON body with a `target_level` field. The levels
in ascending order are `bronze`, `silver`, and `gold`.

Replace `1` with the ID of an existing customer. Upgrade the customer
to `gold`:

```bash
curl -i -X PUT http://localhost:8080/customers/1/upgrade \
  -H 'Content-Type: application/json' \
  -d '{"target_level":"gold"}'
```

Then downgrade the same customer to `silver`:

```bash
curl -i -X PUT http://localhost:8080/customers/1/downgrade \
  -H 'Content-Type: application/json' \
  -d '{"target_level":"silver"}'
```

Both endpoints return `200 OK` and the full customer object, including
`membership_level`. If the target matches the current level, the service
also returns `200 OK`.

| Status | When it occurs |
| --- | --- |
| `400 Bad Request` | The JSON body omits `target_level` or supplies an invalid level. |
| `404 Not Found` | The customer ID does not exist. |
| `409 Conflict` | An upgrade targets a lower level, or a downgrade targets a higher level. |

### Error responses

Registered error handlers return a JSON object with `status`, `error`, and `message` fields. For example, reading a missing customer produces:

```json
{
  "status": 404,
  "error": "Not Found",
  "message": "404 Not Found: Customer with id 999999 was not found"
}
```

| Code | Typical cause |
|------|---------------|
| `400 Bad Request` | Missing fields, malformed JSON, or a failed database write such as a null or blank first name, last name, email, or address field, a malformed email, an invalid state code, a malformed ZIP code, or an unknown membership level. |
| `404 Not Found` | Reading or updating a missing customer, or requesting an unknown URL. |
| `405 Method Not Allowed` | Using a method not registered for a path. |
| `409 Conflict` | Creating a customer, or changing a customer's email, to an email that already belongs to another customer. |
| `415 Unsupported Media Type` | Sending a create/update request without a supported JSON content type. |
| `500 Internal Server Error` | An unexpected server error. |

## Run the tests

### Unit tests

Run the tests from the repository root in the development container.
Make sure PostgreSQL is running and set `DATABASE_URI` to a dedicated
test database. The unit tests drop and recreate tables.

```bash
make test
```

### Selenium BDD tests

In the development container, set `DATABASE_URI` to the test database
and start the service from the repository root:

```bash
honcho start
```

Keep the service running. In a second terminal in the development
container, run the scenarios with headless Chrome:

```bash
BASE_URL=http://localhost:8080 DRIVER=chrome behave
```

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── cli_commands.py    - Flask command to recreate all tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - Factory for testing with fake objects
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for business models
└── test_routes.py         - test suite for service routes
```

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
