# transactions/serializers.py

from rest_framework import serializers

from .models import IncomeOutcomeTransaction, TransferTransaction, BaseTransaction


class BaseTransactionSerializer(serializers.ModelSerializer):
    """Unified serializer for listing all transactions."""

    class Meta:
        model = BaseTransaction
        fields = ['id', 'name', 'amount', 'date', 'note', 'currency', 'detail_url']
        read_only_fields = ['user', 'created_at']


class IncomeOutcomeTransactionSerializer(BaseTransactionSerializer):
    class Meta:
        model = IncomeOutcomeTransaction
        fields = BaseTransactionSerializer.Meta.fields + [
            'transaction_type',
            'balance',
            'created_at',
        ]
        read_only_fields = BaseTransactionSerializer.Meta.read_only_fields + ['user', 'created_at']


class TransferTransactionSerializer(BaseTransactionSerializer):
    class Meta:
        model = TransferTransaction
        fields = BaseTransactionSerializer.Meta.fields + [
            'user',
            'balance_from',
            'balance_to',
            'created_at',
        ]
        read_only_fields = BaseTransactionSerializer.Meta.read_only_fields + ['user', 'created_at']

    def validate(self, data):
        balance_from = data.get('balance_from')
        balance_to = data.get('balance_to')

        if balance_from == balance_to:
            raise serializers.ValidationError("Source and destination balances cannot be the same for a transfer.")

        return data
