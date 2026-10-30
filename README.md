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

## Database Structure

The current database structure is as follows. Only US addresses are supported.

> **Schema change:** the single `address` column was replaced by `street`, `city`, `state` and `postal_code`, and a `membership_level` column was added. Existing data is not migrated: run `flask db-create` to drop and recreate the tables.

| Field | Type |  Description |
|-------|------|-------------|
| `id` | Integer | Primary key, used as `{customer_id}` in URLs. |
| `name` | String, up to 63 characters | Customer name. Cannot be null, empty, or whitespace-only. |
| `street` | String, up to 255 characters | Street address. Cannot be null, empty, or whitespace-only. |
| `city` | String, up to 63 characters | City. Cannot be null, empty, or whitespace-only. |
| `state` | String, 2 characters | US state code, e.g. `NY`. Must be a USPS code (50 states, DC, territories or Freely Associated States); lowercase input is stored uppercase. |
| `postal_code` | String, up to 10 characters | US ZIP code in `12345` or `12345-6789` format. |
| `membership_level` | String | One of `bronze`, `silver`, or `gold`. Defaults to `bronze`. |

Example customer representation:

```json
{
  "id": 1,
  "name": "DevOps",
  "street": "251 Mercer St",
  "city": "New York",
  "state": "NY",
  "postal_code": "10012",
  "membership_level": "bronze"
}
```

## APIs

Examples use `http://localhost:8080`.

### Get Service Information

`GET /`

```bash
curl -i http://localhost:8080/
```

Returns service information and the customers endpoint URL with `200 OK`.

Example response:

```json
{
  "name": "Customer REST API Service",
  "version": "1.0",
  "description": "Create, read, update, delete and list the customers that are registered in the e-commerce store",
  "paths": "http://localhost:8080/customers"
}
```

### Create a Customer

`POST /customers`

```bash
curl -i -X POST http://localhost:8080/customers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "DevOps",
    "street": "251 Mercer St",
    "city": "New York",
    "state": "NY",
    "postal_code": "10012"
  }'
```

Every new customer is created with the `bronze` membership level. `membership_level` is not needed in the request; if a valid level is given, it is ignored. Use [Update a Customer](#update-a-customer) to change the level.

Example response for a newly assigned ID of `1`:

```http
HTTP/1.1 201 CREATED
Content-Type: application/json
Location: http://localhost:8080/customers/1

{
  "id": 1,
  "name": "DevOps",
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
| Missing required field, malformed JSON, or database constraint violation | `400` |
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
    "name": "John",
    "street": "44 W Fourth St",
    "city": "New York",
    "state": "NY",
    "postal_code": "10003",
    "membership_level": "gold"
  }'
```

Provide all address and name fields, including any value you want to keep. `membership_level` is optional; if it is omitted, the current level is kept. Partial updates and `PATCH` requests are not implemented.

Example response body with `200 OK`:

```json
{
  "id": 1,
  "name": "DevOps",
  "street": "251 Mercer St",
  "city": "New York",
  "state": "NY",
  "postal_code": "10012",
  "membership_level": "gold"
}
```

| Result | Status |
|--------|--------|
| Customer updated | `200` |
| Customer does not exist | `404` |
| Missing required field, malformed JSON, or database constraint violation | `400` |

The route checks whether the customer exists before reading the body, so a request for a missing customer returns `404` before body validation.

### Delete a Customer

`DELETE /customers/{customer_id}`

```bash
curl -i -X DELETE http://localhost:8080/customers/1
```

Returns `204 No Content` with an empty body. Deleting an ID that does not exist also returns `204`, making repeated delete requests idempotent.

### List All Customers

`GET /customers`

```bash
curl -i http://localhost:8080/customers
```

Returns a JSON array of all customers with `200 OK`. If no customers exist, returns an empty array `[]`.

Example response:

```json
[
  {
    "id": 1,
    "name": "DevOps",
    "street": "251 Mercer St",
    "city": "New York",
    "state": "NY",
    "postal_code": "10012",
    "membership_level": "bronze"
  }
]
```

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
| `400 Bad Request` | Missing fields, malformed JSON, or a failed database write such as a null or blank name or address field, an invalid state code, a malformed ZIP code, or an unknown membership level. |
| `404 Not Found` | Reading or updating a missing customer, or requesting an unknown URL. |
| `405 Method Not Allowed` | Using a method not registered for a path. |
| `415 Unsupported Media Type` | Sending a create/update request without a supported JSON content type. |
| `500 Internal Server Error` | An unexpected server error. |

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
