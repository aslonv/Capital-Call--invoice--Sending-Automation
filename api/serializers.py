from rest_framework import serializers
from .models import Investor, Bill, CapitalCall
from django.core.exceptions import ValidationError
from stdnum import iban

class InvestorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investor
        fields = '__all__'

class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = '__all__'

class CapitalCallSerializer(serializers.ModelSerializer):
    investor_id = serializers.IntegerField(write_only=True)
    bill_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

    class Meta:
        model = CapitalCall
        fields = '__all__'
        read_only_fields = ('total_amount', 'status')

    def validate(self, data):
        investor_id = data.get('investor_id')
        bill_ids = data.get('bill_ids', [])

        try:
            investor = Investor.objects.get(id=investor_id)
        except Investor.DoesNotExist:
            raise ValidationError('Investor not found')

        bills = Bill.objects.filter(id__in=bill_ids, investor=investor)
        if not bills.exists():
            raise ValidationError('No valid bills found for this investor')

        data['investor'] = investor
        data['bills'] = bills
        data['total_amount'] = sum(bill.amount for bill in bills)

        return data

    def create(self, validated_data):
        bills = validated_data.pop('bills')
        capital_call = CapitalCall.objects.create(
            investor=validated_data['investor'],
            total_amount=validated_data['total_amount'],
            iban=validated_data['iban'],
            status=CapitalCall.VALIDATED
        )
        capital_call.bills.set(bills)
        return capital_call

    def validate_iban(self, value):
        try:
            return iban.validate(value)
        except ValueError:
            raise serializers.ValidationError('Invalid IBAN')