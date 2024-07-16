from django.db import models
from django.utils.timezone import now
from django.core.validators import MinValueValidator, RegexValidator

# Model to represent an investor
class Investor(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    amount_invested = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    investment_date = models.DateField(default=now)

    def __str__(self):
        return self.name

# Model to represent a bill associated with an investor
class Bill(models.Model):
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
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    date = models.DateField()
    due_date = models.DateField()
    fee_percentage = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)

    def __str__(self):
        return f"{self.get_bill_type_display()} - {self.amount} ({self.date})"

# Model to represent a capital call associated with an investor and multiple bills
class CapitalCall(models.Model):
    VALIDATED = 'validated'
    SENT = 'sent'
    PAID = 'paid'
    OVERDUE = 'overdue'

    STATUS_CHOICES = [
        (VALIDATED, 'Validated'),
        (SENT, 'Sent'),
        (PAID, 'Paid'),
        (OVERDUE, 'Overdue')
    ]

    investor = models.ForeignKey(Investor, on_delete=models.CASCADE)
    bills = models.ManyToManyField(Bill)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    iban = models.CharField(
        max_length=34, 
        validators=[RegexValidator(
            regex='^[A-Z]{2}\\d{2}[A-Z0-9]{1,30}$', 
            message='Invalid IBAN format'
        )]
    )
    status = models.CharField(choices=STATUS_CHOICES, max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Capital Call - {self.total_amount} ({self.status})"

    def calculate_total_amount(self):
        """
        Calculate and update the total amount based on associated bills.
        """
        self.total_amount = sum(bill.amount for bill in self.bills.all())
        self.save()
