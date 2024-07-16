
# ARCHIMED Capital Call Automation System Documentation

## 1. Project Overview

The ARCHIMED Capital Call Automation System is a Django-based web application designed to manage investors, bills, and capital calls. It provides functionality for generating bills, creating capital calls, and updating their statuses.

Key features:

* Investor management
* Bill generation
* Capital call creation and management
* RESTful API for data manipulation
* Frontend interface for user interaction

## 2. Backend (Django)

### Models (`api/models.py`)

1. `Investor`:
   * Represents an investor with name, email, amount invested, and investment date.
   * Includes validation for positive investment amounts.
2. `Bill`:
   * Represents a bill associated with an investor.
   * Types: Membership, Upfront, Yearly
   * Includes amount, date, due date, and optional fee percentage.
3. `CapitalCall`:
   * Represents a capital call associated with an investor and multiple bills.
   * Includes total amount, IBAN, status, and timestamps.
   * Status choices: Validated, Sent, Paid, Overdue

### Views (`api/views.py`)

Implements ViewSets for Investor, Bill, and CapitalCall models:

* `InvestorViewSet`: CRUD operations for Investors, includes caching for performance.
* `BillViewSet`: CRUD operations for Bills.
* `CapitalCallViewSet`: CRUD operations for CapitalCalls, includes custom actions for status updates.

### Serializers (`api/serializers.py`)

Defines serializers for model serialization and deserialization:

* `InvestorSerializer`
* `BillSerializer`
* `CapitalCallSerializer`: Includes custom validation for bills and IBAN.

### Utils (`api/utils.py`)

Contains utility functions for fee calculations:

* `calculate_membership_fee()`
* `calculate_upfront_fee()`
* `calculate_yearly_fee()`
* `generate_bills_for_investor()`

### Tasks (`api/tasks.py`)

Defines Celery tasks for asynchronous processing:

* `generate_bills_task()`: Generates bills for an investor asynchronously.

## 3. Frontend

The frontend is implemented using Django templates and JavaScript:

* `frontend/templates/index.html`: Main template for the application interface.
* `frontend/static/css/styles.css`: CSS styles for the frontend.
* `frontend/static/js/scripts.js`: JavaScript for frontend interactivity.

## 4. API Endpoints

* `/api/investors/`: CRUD operations for Investors
* `/api/bills/`: CRUD operations for Bills
* `/api/capital-calls/`: CRUD operations for CapitalCalls
* `/api/investors/{id}/generate_bills/`: Generate bills for a specific investor
* `/api/capital-calls/{id}/update_status/`: Update status of a capital call

## 5. Testing

The project includes comprehensive unit tests and integration tests:

* Model tests: Validate model creation and constraints.
* Utility function tests: Ensure correct fee calculations.
* API tests: Test API endpoints and responses.
* Integration tests: Test full workflow from investor creation to capital call management.
