# api/tasks.py
from celery import shared_task
from .models import Investor
from .utils import generate_bills_for_investor
from decimal import Decimal
from datetime import date, timedelta

@shared_task
def generate_bills_task(investor_id, fee_percentage, bill_date, due_date):
    investor = Investor.objects.get(id=investor_id)
    bills = generate_bills_for_investor(investor, Decimal(fee_percentage), bill_date, due_date)
    return len(bills)