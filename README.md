
Accurate financial calculations necessitate consideration of leap years, especially for pro-rata calculations based on daily investments. This section details how leap year adjustments are integrated into our fee calculation system.

Implementation
Leap year handling is incorporated into the calculate_yearly_fee function at two critical points:

For investments before April 2019: Adjustments ensure correct calculation of days in the first year based on whether it is a leap year.

python
Copy code
if years_since_investment == 0:  # First year
    days_in_year = 366 if investment_date.year % 4 == 0 else 365
    days_invested = (date(investment_date.year, 12, 31) - investment_date).days + 1
    return (Decimal(days_invested) / Decimal(days_in_year)) * fee_percentage * amount_invested
For investments after April 2019: Similar adjustments are made to reflect leap year considerations up to the current date.

python
Copy code
if years_since_investment == 0:  # First year
    days_in_year = 366 if current_date.year % 4 == 0 else 365
    days_invested = (current_date - investment_date).days + 1
    return (Decimal(days_invested) / Decimal(days_in_year)) * fee_percentage * amount_invested
Importance
Accuracy: Ensures precise fee calculations for investments spanning leap years.
Equitability: Guarantees fair charges irrespective of leap year occurrences.
Compliance: Demonstrates adherence to financial regulations by ensuring meticulous calculations.
Edge Case Handling: Properly manages scenarios like investments made on February 29th in leap years.
Enhanced IBAN Validation
Overview
Our system employs a dual-layer validation mechanism for International Bank Account Numbers (IBANs), encompassing both client-side and server-side validation to uphold data integrity.

Frontend Validation
Implementation
Client-side validation utilizes a regular expression to promptly detect incorrectly formatted IBANs:

javascript
Copy code
function validateIBAN(iban) {
    const ibanRegex = /^([A-Z]{2}[ \-]?[0-9]{2})(?=(?:[ \-]?[A-Z0-9]){9,30}$)((?:[ \-]?[A-Z0-9]{3,5}){2,7})([ \-]?[A-Z0-9]{1,3})?$/;
    return ibanRegex.test(iban.replace(/\s/g,''));
}
This validation offers immediate user feedback and reduces unnecessary server requests.

Backend Validation
Implementation
Backend validation utilizes the python-stdnum library for comprehensive validation, including country-specific rules and check digits:

python
Copy code
from stdnum import iban

class IBANField(models.CharField):
    def clean(self, value, model_instance):
        value = super().clean(value, model_instance)
        try:
            return iban.validate(value)
        except ValueError:
            raise ValidationError('Invalid IBAN')
This approach ensures all IBANs in our database adhere to international banking standards.

Security Benefits
Immediate User Feedback: Enhances user experience by promptly identifying IBAN format errors.
Server Load Reduction: Minimizes unnecessary server and database operations.
Comprehensive Validation: Ensures strict adherence to global IBAN standards, regardless of frontend validation status.
Caching Implementation
Endpoints
Caching is implemented for the following endpoints to optimize performance:

Individual investor details retrieval
Investor details update operations
Cache Strategy
Investor details are cached for one hour post retrieval, with automatic updates triggered upon API-based modifications. This strategy efficiently reduces database load and improves response times for frequently accessed data.

Background Tasks with Celery
Overview
Celery is leveraged for executing asynchronous, time-intensive tasks such as generating multiple bills, thereby enhancing API responsiveness and scalability.

Benefits
Enhanced Responsiveness: Enables the API to handle concurrent requests effectively.
Scalability: Distributes workload across multiple workers, enhancing system capacity.
Reliability: Ensures task completion even during system interruptions or timeouts.
Implementation
Celery-based background tasks are initiated via API calls, with results stored and accessible upon task completion. This approach optimizes performance and enriches user interaction by ensuring non-blocking task execution.

