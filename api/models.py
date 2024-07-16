# api/models.py

from stdnum import iban
from django.db import models
from decimal import Decimal
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator

# Model to represent an investor
class Investor(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    amount_invested = models.DecimalField(max_digits=10, decimal_places=2)
    investment_date = models.DateField()

    def clean(self):
        if self.amount_invested <= 0:
            raise ValidationError({'amount_invested': 'Amount invested must be positive.'})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

# Model to represent a bill associated with an investor
class Bill(models.Model):
    class Meta:
        ordering = ['id']

    MEMBERSHIP = 'membership'
    UPFRONT = 'upfront'
    YEARLY = 'yearly'

    BILL_TYPES = [
        (MEMBERSHIP, 'Membership'),
        (UPFRONT, 'Upfront Fees'),
        (YEARLY, 'Yearly Fees')
    ]

    investor = models.ForeignKey(Investor, on_delete=models.CASCADE)
    bill_type = models.CharField(choices=BILL_TYPES, max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    date = models.DateField()
    due_date = models.DateField()
    fee_percentage = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)

    def __str__(self):
        return f"{self.get_bill_type_display()} - {self.amount} ({self.date})"
    
class IBANField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 34)
        super().__init__(*args, **kwargs)

    def clean(self, value, model_instance):
        value = super().clean(value, model_instance)
        try:
            return iban.validate(value)
        except ValueError:
            raise ValidationError('Invalid IBAN')

# Model to represent a capital call associated with an investor and multiple bills
class CapitalCall(models.Model):
    class Status(models.TextChoices):
        VALIDATED = 'validated', 'Validated'
        SENT = 'sent', 'Sent'
        PAID = 'paid', 'Paid'
        OVERDUE = 'overdue', 'Overdue'

    investor = models.ForeignKey('Investor', on_delete=models.CASCADE)
    bills = models.ManyToManyField('Bill')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    iban = IBANField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.VALIDATED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Capital Call - {self.total_amount} ({self.get_status_display()})"

    def calculate_total_amount(self):
        self.total_amount = self.bills.aggregate(total=models.Sum('amount'))['total'] or 0
        self.save(update_fields=['total_amount'])

    def clean(self):
        super().clean()
        if self.status not in self.Status.values:
            raise ValidationError({'status': 'Invalid status choice.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_status_choices(cls):
        return cls.Status.choices