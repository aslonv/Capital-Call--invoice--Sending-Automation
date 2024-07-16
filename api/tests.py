from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ErrorDetail
from api import get_models, get_utils
import math

Investor, Bill, CapitalCall = get_models()
calculate_membership_fee, calculate_upfront_fee, calculate_yearly_fee = get_utils()

class ModelTests(TestCase):
    def setUp(self):
        self.investor = Investor.objects.create(
            name="Test Investor",
            email="test@example.com",
            amount_invested=Decimal('100000.00'),
            investment_date=date(2022, 1, 1)
        )

    def test_investor_creation(self):
        self.assertEqual(self.investor.name, "Test Investor")
        self.assertEqual(self.investor.email, "test@example.com")
        self.assertEqual(self.investor.amount_invested, Decimal('100000.00'))
        self.assertEqual(self.investor.investment_date, date(2022, 1, 1))

    def test_bill_creation(self):
        bill = Bill.objects.create(
            investor=self.investor,
            bill_type='membership',
            amount=Decimal('3000.00'),
            date=date(2023, 1, 1),
            due_date=date(2023, 1, 31)
        )
        self.assertEqual(bill.investor, self.investor)
        self.assertEqual(bill.bill_type, 'membership')
        self.assertEqual(bill.amount, Decimal('3000.00'))

    def test_capital_call_creation(self):
        capital_call = CapitalCall.objects.create(
            investor=self.investor,
            total_amount=Decimal('5000.00'),
            iban='DE89370400440532013000',
            status=CapitalCall.Status.VALIDATED
        )
        self.assertEqual(capital_call.investor, self.investor)
        self.assertEqual(capital_call.total_amount, Decimal('5000.00'))
        self.assertEqual(capital_call.iban, 'DE89370400440532013000')
        self.assertEqual(capital_call.status, CapitalCall.Status.VALIDATED)

class UtilityFunctionTests(TestCase):
    def test_calculate_membership_fee(self):
        self.assertEqual(calculate_membership_fee(Decimal('40000.00')), Decimal('3000.00'))
        self.assertEqual(calculate_membership_fee(Decimal('60000.00')), Decimal('0.00'))

    def test_calculate_upfront_fee(self):
        self.assertEqual(
            calculate_upfront_fee(Decimal('0.01'), Decimal('100000.00')),
            Decimal('5000.00')
        )

    def test_calculate_yearly_fee(self):
        # Test for investment before 2019/04
        fee_before_2019 = calculate_yearly_fee(date(2018, 1, 1), Decimal('0.01'), Decimal('100000.00'), current_date=date(2023, 1, 1))
        self.assertAlmostEqual(fee_before_2019, Decimal('1000.00'), places=2)

        # Test for investment after 2019/04
        # First year (prorated)
        fee_after_2019_year1 = calculate_yearly_fee(date(2020, 7, 1), Decimal('0.01'), Decimal('100000.00'), current_date=date(2020, 12, 31))
        self.assertTrue(math.isclose(fee_after_2019_year1, Decimal('500.00'), rel_tol=0.01))  # 1% relative tolerance

        # Second year (full fee)
        fee_after_2019_year2 = calculate_yearly_fee(date(2020, 7, 1), Decimal('0.01'), Decimal('100000.00'), current_date=date(2021, 12, 31))
        self.assertAlmostEqual(fee_after_2019_year2, Decimal('1000.00'), places=2)

        # Third year (fee - 0.20%)
        fee_after_2019_year3 = calculate_yearly_fee(date(2020, 7, 1), Decimal('0.01'), Decimal('100000.00'), current_date=date(2022, 12, 31))
        self.assertAlmostEqual(fee_after_2019_year3, Decimal('800.00'), places=2)

        # Fourth year (fee - 0.50%)
        fee_after_2019_year4 = calculate_yearly_fee(date(2020, 7, 1), Decimal('0.01'), Decimal('100000.00'), current_date=date(2023, 12, 31))
        self.assertAlmostEqual(fee_after_2019_year4, Decimal('500.00'), places=2)

        # Fifth year and beyond (fee - 1%)
        fee_after_2019_year5 = calculate_yearly_fee(date(2020, 7, 1), Decimal('0.01'), Decimal('100000.00'), current_date=date(2024, 12, 31))
        self.assertAlmostEqual(fee_after_2019_year5, Decimal('0.00'), places=2)

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
        url = reverse('capitalcall-list')
        data = {
            'investor': self.investor.id,
            'bills': [bill.id],
            'iban': 'DE89370400440532013000',
            'status': CapitalCall.Status.VALIDATED
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CapitalCall.objects.count(), 1)

    def test_update_capital_call_status(self):
        capital_call = CapitalCall.objects.create(
            investor=self.investor,
            total_amount=Decimal('5000.00'),
            iban='DE89370400440532013000',
            status=CapitalCall.Status.VALIDATED
        )
        url = reverse('capitalcall-update-status', kwargs={'pk': capital_call.id})
        data = {'status': CapitalCall.Status.SENT}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        capital_call.refresh_from_db()
        self.assertEqual(capital_call.status, CapitalCall.Status.SENT)

class AdvancedModelTests(TestCase):
    def setUp(self):
        self.investor = Investor.objects.create(
            name="Advanced Test Investor",
            email="advancedtest@example.com",
            amount_invested=Decimal('100000.00'),
            investment_date=date(2022, 1, 1)
        )

    def test_investor_negative_investment(self):
        with self.assertRaises(ValidationError):
            Investor.objects.create(
                name="Negative Investor",
                email="negative@example.com",
                amount_invested=Decimal('-10000.00'),
                investment_date=date(2022, 1, 1)
            )

    def test_bill_future_date(self):
        future_date = date.today() + timedelta(days=30)
        bill = Bill.objects.create(
            investor=self.investor,
            bill_type='membership',
            amount=Decimal('3000.00'),
            date=future_date,
            due_date=future_date + timedelta(days=30)
        )
        self.assertEqual(bill.date, future_date)

    def test_capital_call_invalid_status(self):
        with self.assertRaises(ValidationError):
            CapitalCall.objects.create(
                investor=self.investor,
                total_amount=Decimal('5000.00'),
                iban='DE89370400440532013000',
                status='invalid_status'
            )

class AdvancedAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.investor = Investor.objects.create(
            name="API Advanced Test Investor",
            email="apiadvancedtest@example.com",
            amount_invested=Decimal('100000.00'),
            investment_date=date(2022, 1, 1)
        )

    def test_create_capital_call_invalid_iban(self):
        bill = Bill.objects.create(
            investor=self.investor,
            bill_type='membership',
            amount=Decimal('3000.00'),
            date=date(2023, 1, 1),
            due_date=date(2023, 1, 31)
        )
        url = reverse('capitalcall-list')
        data = {
            'investor': self.investor.id,
            'bills': [bill.id],
            'iban': 'INVALID_IBAN',
            'status': CapitalCall.Status.VALIDATED
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('iban', response.data)

    def test_create_capital_call_bills_from_different_investor(self):
        other_investor = Investor.objects.create(
            name="Other Investor",
            email="other@example.com",
            amount_invested=Decimal('50000.00'),
            investment_date=date(2022, 1, 1)
        )
        bill = Bill.objects.create(
            investor=other_investor,
            bill_type='membership',
            amount=Decimal('3000.00'),
            date=date(2023, 1, 1),
            due_date=date(2023, 1, 31)
        )
        url = reverse('capitalcall-list')
        data = {
            'investor': self.investor.id,
            'bills': [bill.id],
            'iban': 'DE89370400440532013000',
            'status': CapitalCall.Status.VALIDATED
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_generate_bills_invalid_fee_percentage(self):
        url = reverse('investor-generate-bills', kwargs={'pk': self.investor.id})
        data = {'fee_percentage': '-0.01'}  # Negative fee percentage
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class IntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.investor = Investor.objects.create(
            name="Integration Test Investor",
            email="integrationtest@example.com",
            amount_invested=Decimal('100000.00'),
            investment_date=date(2022, 1, 1)
        )

    def test_full_workflow(self):
        # Step 1: Generate bills for the investor
        generate_bills_url = reverse('investor-generate-bills', kwargs={'pk': self.investor.id})
        generate_bills_data = {'fee_percentage': '0.01'}
        response = self.client.post(generate_bills_url, generate_bills_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Step 2: Retrieve the generated bills
        bills_url = reverse('bill-list')
        response = self.client.get(bills_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        bills_data = response.data
        
        self.assertIn('results', bills_data, "Expected paginated response")
        bills = bills_data['results']
        self.assertTrue(len(bills) > 0)
        
        # Check if bills is a dict with 'results' key (for paginated response)
        if isinstance(bills, dict) and 'results' in bills:
            bills = bills['results']
        
        self.assertTrue(len(bills) > 0)
        
        # Step 3: Create a capital call using the generated bills
        capital_call_url = reverse('capitalcall-list')
        capital_call_data = {
            'investor': self.investor.id,
            'bills': [bill['id'] for bill in bills],
            'iban': 'DE89370400440532013000',
            'status': CapitalCall.Status.VALIDATED
        }
        response = self.client.post(capital_call_url, capital_call_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        capital_call_id = response.data['id']
        
        # Step 4: Update the status of the capital call
        update_status_url = reverse('capitalcall-update-status', kwargs={'pk': capital_call_id})
        update_status_data = {'status': CapitalCall.Status.SENT}
        response = self.client.post(update_status_url, update_status_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], CapitalCall.Status.SENT)
        
        # Step 5: Verify the final state
        capital_call = CapitalCall.objects.get(id=capital_call_id)
        self.assertEqual(capital_call.status, CapitalCall.Status.SENT)
        self.assertEqual(capital_call.bills.count(), len(bills))
        self.assertEqual(capital_call.investor, self.investor)