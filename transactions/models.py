from django.conf import settings
from django.db import models
from django.urls import reverse
from rest_framework.exceptions import ValidationError


class BaseTransaction(models.Model):
    class Meta:
        db_table = 'transactions'

    """Abstract base class for all transactions."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions")
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField()
    note = models.TextField(blank=True, null=True)
    currency = models.CharField(max_length=3, choices=settings.CURRENCIES, default="EUR")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def detail_url(self):
        if hasattr(self, 'incomeoutcometransaction'):
            return reverse('income_outcome_transaction-detail', args=[self.incomeoutcometransaction.id])
        elif hasattr(self, 'transfertransaction'):
            return reverse('transfer_transaction-detail', args=[self.transfertransaction.id])
        return None

    def __str__(self):
        return f"{self.user.username} - {self.name} ({self.amount} {self.currency})"


# transactions/models.py

# transactions/models.py

class IncomeOutcomeTransaction(BaseTransaction):
    class Meta:
        db_table = 'income_outcome_transactions'

    class TransactionType(models.TextChoices):
        INCOME = 'income'
        OUTCOME = 'outcome'

    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices, default=TransactionType.OUTCOME)
    balance = models.ForeignKey('balances.Balance', on_delete=models.CASCADE,
                                related_name="income_outcome_transactions", null=True, blank=True)


class TransferTransaction(BaseTransaction):
    class Meta:
        db_table = 'transfer_transactions'

    """Model for transfer transactions."""
    balance_from = models.ForeignKey('balances.Balance', on_delete=models.CASCADE, related_name="transfers_sent")
    balance_to = models.ForeignKey('balances.Balance', on_delete=models.CASCADE, related_name="transfers_received")

    def clean(self):
        if self.balance_from == self.balance_to:
            raise ValidationError("Source and destination balances cannot be the same for a transfer.")
