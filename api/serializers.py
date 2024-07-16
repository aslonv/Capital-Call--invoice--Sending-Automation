from rest_framework import serializers
from .models import Investor, Bill, CapitalCall
from .utils import generate_bills_for_investor
from django.utils import timezone
from decimal import Decimal, InvalidOperation

class InvestorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investor
        fields = '__all__'

    def generate_bills(self, investor_id, fee_percentage):
        try:
            investor = Investor.objects.get(id=investor_id)
            bill_date = timezone.now().date()
            due_date = bill_date + timezone.timedelta(days=30)
            
            # Convert fee_percentage to Decimal
            try:
                fee_percentage = Decimal(str(fee_percentage))
            except InvalidOperation:
                return {'error': 'Invalid fee percentage'}

            bills = generate_bills_for_investor(investor, fee_percentage, bill_date, due_date)
            return {'message': f'{len(bills)} bills generated for {investor.name}'}
        except Investor.DoesNotExist:
            return {'error': 'Investor not found'}
        except Exception as e:
            return {'error': str(e)}

class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = '__all__'

class CapitalCallSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapitalCall
        fields = '__all__'

    def create_for_investor(self, data):
        investor_id = data.get('investor_id')
        bill_ids = data.get('bill_ids', [])

        try:
            investor = Investor.objects.get(id=investor_id)
            bills = Bill.objects.filter(id__in=bill_ids, investor=investor)
            
            if not bills.exists():
                return {'error': 'No valid bills found for this investor'}

            total_amount = sum(bill.amount for bill in bills)
            
            capital_call = CapitalCall.objects.create(
                investor=investor,
                total_amount=total_amount,
                iban=data.get('iban'),
                status=CapitalCall.VALIDATED
            )
            capital_call.bills.set(bills)

            return self.to_representation(capital_call)
        except Investor.DoesNotExist:
            return {'error': 'Investor not found'}

    def update_status(self, capital_call_id, new_status):
        try:
            capital_call = CapitalCall.objects.get(id=capital_call_id)
            
            if new_status not in dict(CapitalCall.STATUS_CHOICES):
                return {'error': 'Invalid status'}

            capital_call.status = new_status
            capital_call.save()

            return self.to_representation(capital_call)
        except CapitalCall.DoesNotExist:
            return {'error': 'Capital Call not found'}
