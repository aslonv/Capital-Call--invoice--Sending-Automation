**Documentation**

Added leap year

Certainly! I'd be happy to document the inclusion of leap year considerations in our fee calculation. This is an important aspect of accurate financial calculations, especially when dealing with daily pro-rata calculations.

# Leap Year Handling in Fee Calculations

## Overview

In our `calculate_yearly_fee` function, we've incorporated leap year handling to ensure accurate fee calculations, particularly for the first year of investment when we need to calculate fees based on the number of days invested.

## Implementation

The leap year handling is implemented in two places within the `calculate_yearly_fee` function:

1. For investments before April 2019

`if years_since_investment == 0:
    # First year
    days_in_year = 366 if investment_date.year % 4 == 0 else 365
    days_invested = (date(investment_date.year, 12, 31) - investment_date).days + 1
    return (Decimal(days_invested) / Decimal(days_in_year)) * fee_percentage * amount_invested`

2. For investments after April 2019:

`if years_since_investment == 0:     # First year     days_in_year = 366 if current_date.year % 4 == 0 else 365     days_invested = (current_date - investment_date).days + 1     return (Decimal(days_invested) / Decimal(days_in_year)) * fee_percentage * amount_invested`

    1.**Determining Leap Years** :
	We use the simple rule that a year is a leap year if it's divisible by 4. This is done using the modulo operator:
	`days_in_year = 366 if investment_date.year % 4 == 0 else 365`

    Accurate for all years from 1901 to 2099

**
    2. Calculating Days in First Year** :

    - For pre-2019 investments, we calculate the days from the investment date to the end of that year.

    - For post-2019 investments, we calculate the days from the investment date to the current date.

**
    3. Pro-rata Calculation**

    We use the correct number of days in the year (365 or 366) as the denominator when calculating the pro-rata fee for partial years:

`return (Decimal(days_invested) / Decimal(days_in_year)) * fee_percentage * amount_invested`

## Importance

1. **Accuracy** : Leap year handling ensures that fees are calculated accurately, especially for investments made in or spanning leap years. Without this, we could be off by 1/366 of the annual fee for investments in leap years.
2. **Fairness** : It ensures that investors are charged fairly, regardless of whether their investment year is a leap year or not.
3. **Compliance** : Many financial regulations require precise calculations. Accounting for leap years demonstrates attention to detail and commitment to accuracy.
4. **Edge Case Handling** : It correctly handles the edge case of investments made on February 29th in leap years.

By implementing CSRF protection in this manner, your frontend JavaScript code ensures that it complies with Django's CSRF protection mechanism, thereby preventing cross-site request forgery attacks.



# Enhanced IBAN Validation Documentation

## Overview

We've implemented a two-tier validation system for International Bank Account Numbers (IBANs) in our application. This system includes both client-side (frontend) and server-side (backend) validation to ensure the integrity and correctness of IBAN data entered by users.

## Frontend Validation

### Implementation

**function**validateIBAN**(**iban**)**{
**const** ibanRegex **=**/**^([A-Z]{2}[ \-]?[0-9]{2})(?=(?:[ \-]?[A-Z0-9]){9,30}$)((?:[ \-]?[A-Z0-9]{3,5}){2,7})([ \-]?[A-Z0-9]{1,3})?$**/**;**
**return** ibanRegex**.**test**(**iban**.**replace**(**/**\s**/**g**,**''**)**)**;
**}**

This function is called before sending IBAN data to the server:

**function**createCapitalCall**(**)**{**
**// ...**
**const** iban **=**prompt**(**"Enter IBAN:"**)**;
**if**(**!**validateIBAN**(**iban**)**)**{**
**alert**(**'Invalid IBAN format'**)**;**
**return**;
**}**
**// ... continue with API call**
**}**


Security Benefits


* **Immediate User Feedback** : Users receive instant feedback if they enter an incorrectly formatted IBAN, improving user experience and reducing server load.
* **Reduced Server Load** : By catching obvious format errors client-side, we reduce unnecessary server requests and database operations.


In the backend, we've implemented a more robust validation using the `python-stdnum` library:


**from** stdnum **import** iban

**class**IBANField**(**models**.**CharField**)**:
**def**clean**(**self**,** value**,** model_instance**)**:
        value **=**super**(**)**.**clean**(**value**,** model_instance**)**
**try**:
**return** iban**.**validate**(**value**)**
**except** ValueError**:**
**raise** ValidationError**(**'Invalid IBAN'**)**

**class**CapitalCall**(**models**.**Model**)**:
    iban **=** IBANField**(**)
**# ...**



And in the serializer:

class CapitalCallSerializer(serializers.ModelSerializer):
    def validate_iban(self, value):
        from stdnum import iban
        try:
            return iban.validate(value)
        except ValueError:
            raise serializers.ValidationError('Invalid IBAN')



* **Comprehensive Validation** : The `python-stdnum` library performs checks beyond just the format, including country-specific rules and check digits.
* **Up-to-date Rules** : The library is maintained and updated, ensuring our validation stays current with international banking standards.
* **Consistency** : Ensures all IBANs in the database meet a standardized level of validity.
* **Protection Against Bypassed Frontend Validation** : Even if a user bypasses or manipulates the frontend validation, the backend still enforces strict IBAN validity.
