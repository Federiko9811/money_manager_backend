from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings

from balances.models import Balance


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('outgoing', 'Outgoing'),
        ('incoming', 'Incoming'),
        ('transfer', 'Transfer'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions")
    balance_from = models.ForeignKey(Balance, on_delete=models.CASCADE, related_name="transactions")
    balance_to = models.ForeignKey(Balance, null=True, blank=True, on_delete=models.CASCADE, related_name="transfers")
    category = models.ForeignKey("categories.Category", on_delete=models.SET_NULL, null=True, blank=True)

    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    date = models.DateTimeField()
    note = models.TextField(blank=True, null=True)
    currency = models.CharField(max_length=3, choices=settings.CURRENCIES, default="USD")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.name} ({self.transaction_type} - {self.currency})"
