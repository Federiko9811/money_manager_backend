from rest_framework import serializers

from balances.models import Balance
from categories.models import Category
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Display user as a string (e.g., username)
    balance_from = serializers.PrimaryKeyRelatedField(queryset=Balance.objects.all(), allow_null=True, required=False)
    balance_to = serializers.PrimaryKeyRelatedField(queryset=Balance.objects.all(), allow_null=True, required=False)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), allow_null=False, required=True
    )  # Category is required

    class Meta:
        model = Transaction
        fields = [
            'id',
            'user',  # Read-only field
            'balance_from',
            'balance_to',
            'category',
            'name',
            'amount',
            'transaction_type',
            'date',
            'note',
            'currency',
            'created_at',
        ]
        read_only_fields = ['created_at', 'user']  # Ensure these fields are read-only

    def validate(self, data):
        """
        Custom validation for transaction type-specific rules.
        """
        transaction_type = data.get('transaction_type')
        balance_from = data.get('balance_from')
        balance_to = data.get('balance_to')

        if transaction_type == 'transfer':
            if not balance_to:
                raise serializers.ValidationError(
                    {"balance_to": "A 'transfer' transaction requires a 'balance_to' field."})
            if balance_from == balance_to:
                raise serializers.ValidationError("Source and destination balances cannot be the same for a transfer.")
        elif transaction_type == 'incoming':
            if balance_from:
                raise serializers.ValidationError(
                    {"balance_from": "An 'incoming' transaction cannot have a 'balance_from' field."})
        elif transaction_type == 'outgoing':
            if balance_to:
                raise serializers.ValidationError(
                    {"balance_to": "An 'outgoing' transaction cannot have a 'balance_to' field."})

        return data
