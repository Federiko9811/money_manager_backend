from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import IncomeOutcomeTransaction, TransferTransaction


@receiver(post_save, sender=IncomeOutcomeTransaction)
@receiver(post_delete, sender=IncomeOutcomeTransaction)
def update_balance_on_transaction_change(sender, instance, **kwargs):
    """Update balance when an income/outcome transaction is created, updated, or deleted."""
    if instance.balance:
        instance.balance.update_amount()


@receiver(post_save, sender=TransferTransaction)
@receiver(post_delete, sender=TransferTransaction)
def update_balances_on_transfer_change(sender, instance, **kwargs):
    """Update balances when a transfer transaction is created, updated, or deleted."""
    instance.balance_from.update_amount()
    instance.balance_to.update_amount()
