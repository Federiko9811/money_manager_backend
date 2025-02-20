from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum

User = get_user_model()


class Balance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="balances")
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)  # Store amount
    currency = models.CharField(max_length=3, choices=settings.CURRENCIES, default="EUR")
    created_at = models.DateTimeField(auto_now_add=True)

    def update_amount(self):
        """Recalculate and update the balance amount based on transactions."""
        income = self.income_outcome_transactions.filter(transaction_type='income').aggregate(Sum('amount'))[
                     'amount__sum'] or 0
        outcome = self.income_outcome_transactions.filter(transaction_type='outcome').aggregate(Sum('amount'))[
                      'amount__sum'] or 0
        transfers_in = self.transfers_received.aggregate(Sum('amount'))['amount__sum'] or 0
        transfers_out = self.transfers_sent.aggregate(Sum('amount'))['amount__sum'] or 0

        self.amount = (income + transfers_in) - (outcome + transfers_out)
        self.save(update_fields=['amount'])

    def __str__(self):
        return f"{self.user.username} - {self.name} ({self.currency}) - {self.amount}"
