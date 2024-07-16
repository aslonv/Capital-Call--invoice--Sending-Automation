# populate_data.py

import os
import django
from api.models import Investor, Bill, CapitalCall
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ARCHIMED.settings')
django.setup()

def populate():
    # Create Investor
    investor = Investor.objects.create(name='Mr. Ronald McDonald', email='ronald.mcdonald@abc.com')

    # Create Membership Bill
    membership_bill = Bill.objects.create(
        investor=investor,
        bill_type='membership',
        amount=3000,  # Yearly subscription amount as per the case study
        date=date(2023, 1, 1),
        due_date=date(2023, 1, 31)
    )

    # Create Capital Call
    capital_call = CapitalCall.objects.create(
        investor=investor,
        total_amount=25000,  # Total amount for the capital call as per the case study
        iban='FR7630006000011234567890189',
        status='validated'  # Assuming it's initially validated as per the case study
    )
    capital_call.bills.add(membership_bill)

if __name__ == '__main__':
    print("Populating data...")
    populate()
    print("Data population complete.")