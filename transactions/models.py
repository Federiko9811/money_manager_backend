import hashlib
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from rest_framework.exceptions import ValidationError

User = get_user_model()


class BaseTransaction(models.Model):
    class Meta:
        db_table = 'transactions'

    """Abstract base class for all transactions."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    category = models.ForeignKey('categories.Category', on_delete=models.CASCADE, related_name="transactions")
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

    transaction_hash = models.CharField(
        max_length=64,
        unique=True,
        null=True,
        blank=True
    )

    def generate_transaction_hash(self):
        """Generate a unique transaction hash"""
        return hashlib.sha256(
            f"{self.user.id}{self.amount}{self.date}{self.created_at}".encode()
        ).hexdigest()

    def save(self, *args, **kwargs):
        if not self.transaction_hash:
            self.transaction_hash = self.generate_transaction_hash()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.category.name} ({self.amount} {self.currency})"


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
