# api/management/commands/generate_invoices.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import Investor, Bill
from api.utils import calculate_membership_fee, calculate_upfront_fee, calculate_yearly_fee
from decimal import Decimal

class Command(BaseCommand):
    help = 'Generates invoices (bills) for investors based on fee calculations'

    def handle(self, *args, **kwargs):
        investors = Investor.objects.all()

        for investor in investors:
            # Calculate fees
            amount_invested = investor.amount_invested
            fee_percentage = investor.fee_percentage or Decimal('0.01')  # Default fee percentage if not provided

            membership_fee = calculate_membership_fee(amount_invested)
            upfront_fee = calculate_upfront_fee(fee_percentage, amount_invested)
            yearly_fee = calculate_yearly_fee(investor.investment_date, fee_percentage, amount_invested)

            # Create bills for the investor
            Bill.objects.create(
                investor=investor,
                bill_type='membership',
                amount=membership_fee,
                date=timezone.now().date(),
                due_date=(timezone.now().date() + timedelta(days=30))
            )

            Bill.objects.create(
                investor=investor,
                bill_type='upfront',
                amount=upfront_fee,
                date=timezone.now().date(),
                due_date=(timezone.now().date() + timedelta(days=30)),
                fee_percentage=fee_percentage
            )

            Bill.objects.create(
                investor=investor,
                bill_type='yearly',
                amount=yearly_fee,
                date=timezone.now().date(),
                due_date=(timezone.now().date() + timedelta(days=30)),
                fee_percentage=fee_percentage
            )

            self.stdout.write(self.style.SUCCESS(f'Invoices generated for {investor.name}'))

        self.stdout.write(self.style.SUCCESS('Invoice generation completed successfully'))
