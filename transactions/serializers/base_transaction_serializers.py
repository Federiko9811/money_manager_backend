# transactions/serializers.py

from rest_framework import serializers

from transactions.models import BaseTransaction


class BaseTransactionSerializer(serializers.ModelSerializer):
    """Unified serializer for listing all transactions."""
    category = serializers.StringRelatedField()

    class Meta:
        model = BaseTransaction
        fields = ['id', 'category', 'amount', 'date', 'note', 'currency', 'detail_url']
        read_only_fields = ['user', 'created_at']
