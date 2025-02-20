from rest_framework import serializers

from balances.models import Balance
from categories.models import Category
from transactions.models import TransferTransaction
from transactions.serializers.base_transaction_serializers import BaseTransactionSerializer


class CreateTransferTransactionSerializer(BaseTransactionSerializer):
    balance_from = serializers.PrimaryKeyRelatedField(queryset=Balance.objects.all())
    balance_to = serializers.PrimaryKeyRelatedField(queryset=Balance.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

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


class TransferTransactionSerializer(BaseTransactionSerializer):
    balance_from = serializers.StringRelatedField()
    balance_to = serializers.StringRelatedField()
    category = serializers.StringRelatedField()

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
