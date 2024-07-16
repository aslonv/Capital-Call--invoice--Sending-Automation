# api/utils.py

from datetime import datetime, date
from decimal import Decimal

def calculate_membership_fee(amount_invested):
    return Decimal('0') if amount_invested > Decimal('50000') else Decimal('3000.00')

def calculate_upfront_fee(fee_percentage, amount_invested):
    return Decimal(str(fee_percentage)) * amount_invested * Decimal('5')

from decimal import Decimal
from datetime import date

def calculate_yearly_fee(investment_date, fee_percentage, amount_invested, current_date=None):
    fee_percentage = Decimal(str(fee_percentage))
    amount_invested = Decimal(str(amount_invested))
    current_date = current_date or date.today()
    years_since_investment = current_date.year - investment_date.year

    cutoff_date = date(2019, 4, 1)

    if investment_date < cutoff_date:
        # Yearly fees before 2019/04
        if years_since_investment == 0:
            days_in_year = 366 if investment_date.year % 4 == 0 else 365
            days_invested = (date(investment_date.year, 12, 31) - investment_date).days + 1
            return (Decimal(days_invested) / Decimal(days_in_year)) * fee_percentage * amount_invested
        else:
            return fee_percentage * amount_invested
    else:
        # Yearly fees after 2019/04
        if years_since_investment == 0:
            days_in_year = 366 if investment_date.year % 4 == 0 else 365
            days_invested = (date(investment_date.year, 12, 31) - investment_date).days + 1
            return (Decimal(days_invested) / Decimal(days_in_year)) * fee_percentage * amount_invested
        elif years_since_investment == 1:
            return fee_percentage * amount_invested
        elif years_since_investment == 2:
            return (fee_percentage - Decimal('0.0020')) * amount_invested
        elif years_since_investment == 3:
            return (fee_percentage - Decimal('0.0050')) * amount_invested
        else:
            return (fee_percentage - Decimal('0.0100')) * amount_invested

def generate_bills_for_investor(investor, fee_percentage, bill_date, due_date):
    from .models import Bill  # Importing here to avoid circular import
    fee_percentage = Decimal(str(fee_percentage))

    membership_fee = calculate_membership_fee(investor.amount_invested)
    upfront_fee = calculate_upfront_fee(fee_percentage, investor.amount_invested)
    yearly_fee = calculate_yearly_fee(investor.investment_date, fee_percentage, investor.amount_invested)

    bills = [
        Bill(investor=investor, bill_type='membership', amount=membership_fee, date=bill_date, due_date=due_date),
        Bill(investor=investor, bill_type='upfront', amount=upfront_fee, date=bill_date, due_date=due_date, fee_percentage=fee_percentage),
        Bill(investor=investor, bill_type='yearly', amount=yearly_fee, date=bill_date, due_date=due_date, fee_percentage=fee_percentage),
    ]

    return Bill.objects.bulk_create(bills)