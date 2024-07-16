# api/serializers.py

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
    investor = serializers.PrimaryKeyRelatedField(queryset=Investor.objects.all())
    bills = serializers.PrimaryKeyRelatedField(many=True, queryset=Bill.objects.all())

    class Meta:
        model = CapitalCall
        fields = ['id', 'investor', 'bills', 'total_amount', 'iban', 'status']
        read_only_fields = ['total_amount', 'status']

    def create(self, validated_data):
        bills = validated_data.pop('bills')
        total_amount = sum(bill.amount for bill in bills)
        capital_call = CapitalCall.objects.create(
            investor=validated_data['investor'],
            total_amount=total_amount,
            iban=validated_data['iban'],
            status=CapitalCall.Status.VALIDATED
        )
        capital_call.bills.set(bills)
        return capital_call

    def validate(self, data):
        investor = data.get('investor')
        bills = data.get('bills')

        if not bills:
            raise serializers.ValidationError("At least one bill is required.")

        if any(bill.investor != investor for bill in bills):
            raise serializers.ValidationError("All bills must belong to the specified investor.")

        return data

    def validate_status(self, value):
        if value not in dict(CapitalCall.Status.choices):
            raise serializers.ValidationError("Invalid status choice.")
        return value

    def validate_iban(self, value):
        from stdnum import iban
        try:
            return iban.validate(value)
        except ValueError:
            raise serializers.ValidationError('Invalid IBAN')