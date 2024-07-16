from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from datetime import date
from api import get_models, get_utils

Investor, Bill, CapitalCall = get_models()
calculate_membership_fee, calculate_upfront_fee, calculate_yearly_fee = get_utils()

class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.investor = Investor.objects.create(
            name="API Test Investor",
            email="apitest@example.com",
            amount_invested=Decimal('100000.00'),
            investment_date=date(2022, 1, 1)
        )

    def test_create_investor(self):
        url = reverse('investor-list')
        data = {
            'name': 'New Investor',
            'email': 'new@example.com',
            'amount_invested': '200000.00',
            'investment_date': '2023-01-01'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Investor.objects.count(), 2)

    def test_generate_bills(self):
        url = reverse('investor-generate-bills', kwargs={'pk': self.investor.id})
        data = {'fee_percentage': '0.01'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('bills generated' in response.data['message'])

    def test_create_capital_call(self):
        bill = Bill.objects.create(
            investor=self.investor,
            bill_type='membership',
            amount=Decimal('3000.00'),
            date=date(2023, 1, 1),
            due_date=date(2023, 1, 31)
        )
        url = reverse('capitalcall-list')  # Changed from 'capitalcall-create-for-investor'
        data = {
            'investor_id': self.investor.id,
            'bill_ids': [bill.id],
            'iban': 'DE89370400440532013000'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CapitalCall.objects.count(), 1)

    def test_update_capital_call_status(self):
        capital_call = CapitalCall.objects.create(
            investor=self.investor,
            total_amount=Decimal('5000.00'),
            iban='DE89370400440532013000',
            status='validated'
        )
        url = reverse('capitalcall-update-status', kwargs={'pk': capital_call.id})
        data = {'status': 'sent'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        capital_call.refresh_from_db()
        self.assertEqual(capital_call.status, 'sent')