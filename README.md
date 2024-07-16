# Additions 

# Leap Year Handling in Fee Calculations

### Overview

Accurate financial calculations necessitate consideration of leap years, especially for pro-rata calculations based on daily investments. This section details how leap year adjustments are integrated into our fee calculation system.

### Implementation

Leap year handling is incorporated into the `calculate_yearly_fee` function at two critical points:

1. **For investments before April 2019** : Adjustments ensure correct calculation of days in the first year based on whether it is a leap year.
2. **For investments after April 2019** : Similar adjustments are made to reflect leap year considerations up to the current date.

# Pro-rata Calculation**

Using the correct number of days in the year (365 or 366) as the denominator when calculating the pro-rata fee for partial years:

`return (Decimal(days_invested) / Decimal(days_in_year)) * fee_percentage * amount_invested`

## Importance

1. **Accuracy** : Leap year handling ensures that fees are calculated accurately, especially for investments made in or spanning leap years. Without this, we could be off by 1/366 of the annual fee for investments in leap years.
2. **Fairness** : It ensures that investors are charged fairly, regardless of whether their investment year is a leap year or not.
3. **Compliance** : Many financial regulations require precise calculations. Accounting for leap years demonstrates attention to detail and commitment to accuracy.
4. **Edge Case Handling** : It correctly handles the edge case of investments made on February 29th in leap years.

CSRF protection implementation - JavaScript code ensures that it complies with Django's CSRF protection mechanism, thereby preventing cross-site request forgery attacks.

# Enhanced IBAN Validation Documentation

Implemented a two-tier validation system for International Bank Account Numbers (IBANs) in our application. This system includes both client-side (frontend) and server-side (backend) validation to ensure the integrity and correctness of IBAN data entered by users.

1. **Accuracy** : Ensures precise fee calculations for investments spanning leap years.
2. **Equitability** : Guarantees fair charges irrespective of leap year occurrences.
3. **Compliance** : Demonstrates adherence to financial regulations by ensuring meticulous calculations.
4. **Edge Case Handling** : Properly manages scenarios like investments made on February 29th in leap years.

## Enhanced IBAN Validation

### Overview

Our system employs a dual-layer validation mechanism for International Bank Account Numbers (IBANs), encompassing both client-side and server-side validation to uphold data integrity.

### Frontend Validation

#### Implementation

Client-side validation utilizes a regular expression to promptly detect incorrectly formatted IBANs:

This validation offers immediate user feedback and reduces unnecessary server requests.

### Backend Validation

#### Implementation

Backend validation utilizes the `python-stdnum` library for comprehensive validation, including country-specific rules and check digits:

This approach ensures all IBANs in our database adhere to international banking standards.

### Security Benefits

* **Immediate User Feedback** : Enhances user experience by promptly identifying IBAN format errors.
* **Server Load Reduction** : Minimizes unnecessary server and database operations.
* **Comprehensive Validation** : Ensures strict adherence to global IBAN standards, regardless of frontend validation status.

## Caching Implementation

### Endpoints

Caching is implemented for the following endpoints to optimize performance:

* Individual investor details retrieval
* Investor details update operations

### Cache Strategy

Investor details are cached for one hour post retrieval, with automatic updates triggered upon API-based modifications. This strategy efficiently reduces database load and improves response times for frequently accessed data.

---

## Background Tasks with Celery

### Overview

Celery is leveraged for executing asynchronous, time-intensive tasks such as generating multiple bills, thereby enhancing API responsiveness and scalability.

### Benefits

* **Enhanced Responsiveness** : Enables the API to handle concurrent requests effectively.
* **Scalability** : Distributes workload across multiple workers, enhancing system capacity.
* **Reliability** : Ensures task completion even during system interruptions or timeouts.

### Implementation

Celery-based background tasks are initiated via API calls, with results stored and accessible upon task completion. This approach optimizes performance and enriches user interaction by ensuring non-blocking task execution.
