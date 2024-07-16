**Documentation**

# Leap Year Handling in Fee Calculations

# Pro-rata Calculation**

Using the correct number of days in the year (365 or 366) as the denominator when calculating the pro-rata fee for partial years:

`return (Decimal(days_invested) / Decimal(days_in_year)) * fee_percentage * amount_invested`

## Importance

1. **Accuracy** : Leap year handling ensures that fees are calculated accurately, especially for investments made in or spanning leap years. Without this, we could be off by 1/366 of the annual fee for investments in leap years.
2. **Fairness** : It ensures that investors are charged fairly, regardless of whether their investment year is a leap year or not.
3. **Compliance** : Many financial regulations require precise calculations. Accounting for leap years demonstrates attention to detail and commitment to accuracy.
4. **Edge Case Handling** : It correctly handles the edge case of investments made on February 29th in leap years.

-- 

CSRF protection implementation - JavaScript code ensures that it complies with Django's CSRF protection mechanism, thereby preventing cross-site request forgery attacks.

# Enhanced IBAN Validation Documentation

Implemented a two-tier validation system for International Bank Account Numbers (IBANs) in our application. This system includes both client-side (frontend) and server-side (backend) validation to ensure the integrity and correctness of IBAN data entered by users.

Security Benefits

* **Immediate User Feedback** : Users receive instant feedback if they enter an incorrectly formatted IBAN, improving user experience and reducing server load.
* **Reduced Server Load** : By catching obvious format errors client-side, we reduce unnecessary server requests and database operations.

--

## Caching

This API implements caching to improve performance for frequently accessed data. Specifically:

- Individual investor details are cached for 1 hour after being retrieved from the database.
- The cache is automatically updated when an investor is modified through the API.
- Caching is currently implemented for the following endpoints:
  - GET /api/investors/{id}/
  - PUT /api/investors/{id}/
  - PATCH /api/investors/{id}/

Note: The caching duration and strategy may be adjusted based on usage patterns and performance requirements.

--

Implpementation of background tasks with Celery for long-running operations like generating multiple bills. 
Improves the responsiveness of the API and handle complex, time-consuming tasks asynchronously. 
