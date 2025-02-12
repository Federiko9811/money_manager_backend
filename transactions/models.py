# Create your models here.
from django.conf import settings
from django.db import models
from rest_framework.exceptions import ValidationError
from simple_history.models import HistoricalRecords

from balances.models import Balance


class Transaction(models.Model):
    TRANSACTION_TYPES = [('outgoing', 'Outgoing'), ('incoming', 'Incoming'), ('transfer', 'Transfer'), ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions")
    balance_from = models.ForeignKey(Balance, null=True, blank=True, on_delete=models.CASCADE,
                                     related_name="transactions")
    balance_to = models.ForeignKey(Balance, null=True, blank=True, on_delete=models.CASCADE, related_name="transfers")
    category = models.ForeignKey("categories.Category", on_delete=models.SET_NULL, null=True, blank=True)

    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    date = models.DateTimeField()
    note = models.TextField(blank=True, null=True)
    currency = models.CharField(max_length=3, choices=settings.CURRENCIES, default="EUR")
    created_at = models.DateTimeField(auto_now_add=True)

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.user.username} - {self.name} ({self.transaction_type} - {self.currency})"

    def clean(self):
        """Custom validation for transaction type-specific rules."""
        if self.transaction_type == 'transfer':
            if not self.balance_to:
                raise ValidationError("A 'transfer' transaction requires a 'balance_to' field.")
            if self.balance_from == self.balance_to:
                raise ValidationError("Source and destination balances cannot be the same for a transfer.")
        elif self.transaction_type == 'incoming':
            if self.balance_from:
                raise ValidationError("An 'incoming' transaction cannot have a 'balance_from' field.")
        elif self.transaction_type == 'outgoing':
            if self.balance_to:
                raise ValidationError("An 'outgoing' transaction cannot have a 'balance_to' field.")

    def save(self, *args, **kwargs):
        """Ensure the clean method is called before saving."""
        self.full_clean()  # Call clean to enforce validation
        super().save(*args, **kwargs)
