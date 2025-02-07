from django.db import models

from core import settings


class Balance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="balances")
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, choices=settings.CURRENCIES, default="EUR")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.name} ({self.currency}) - {self.amount}"
