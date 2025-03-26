from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.db.models import Sum
import logging

logger = logging.getLogger(__name__)


class Balance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="balances")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)  # New field
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, choices=settings.CURRENCIES, default="EUR")
    is_active = models.BooleanField(default=True)  # Soft delete support
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'currency', 'is_active'])
        ]

    def clean(self):
        """Validate currency and amount"""
        if self.amount < 0:
            raise ValidationError(_('Balance amount cannot be negative.'))

    def soft_delete(self):
        """Soft delete the balance"""
        self.is_active = False
        self.save()

    def update_amount(self):
        """Improved balance update method with error handling"""
        try:
            income = self.income_outcome_transactions.filter(
                transaction_type='income',
                balance__is_active=True
            ).aggregate(Sum('amount'))['amount__sum'] or 0

            outcome = self.income_outcome_transactions.filter(
                transaction_type='outcome',
                balance__is_active=True
            ).aggregate(Sum('amount'))['amount__sum'] or 0

            transfers_in = self.transfers_received.filter(
                balance_to__is_active=True
            ).aggregate(Sum('amount'))['amount__sum'] or 0

            transfers_out = self.transfers_sent.filter(
                balance_from__is_active=True
            ).aggregate(Sum('amount'))['amount__sum'] or 0

            self.amount = (income + transfers_in) - (outcome + transfers_out)
            self.save(update_fields=['amount', 'updated_at'])
        except Exception as e:
            # Log the error
            logger.error(f"Error updating balance {self.id}: {e}")
