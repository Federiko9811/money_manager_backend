from rest_framework import serializers

from categories.models import Category
from transactions.models import IncomeOutcomeTransaction
from transactions.serializers.base_transaction_serializers import BaseTransactionSerializer


class CreateIncomeOutcomeTransactionSerializer(BaseTransactionSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = IncomeOutcomeTransaction

        fields = BaseTransactionSerializer.Meta.fields + [
            'transaction_type',
            'balance',
            'created_at',
        ]
        read_only_fields = BaseTransactionSerializer.Meta.read_only_fields + ['user', 'created_at']


class IncomeOutcomeTransactionSerializer(BaseTransactionSerializer):
    class Meta:
        model = IncomeOutcomeTransaction
        fields = BaseTransactionSerializer.Meta.fields + [
            'transaction_type',
            'balance',
            'created_at',
        ]
        read_only_fields = BaseTransactionSerializer.Meta.read_only_fields + ['user', 'created_at']
