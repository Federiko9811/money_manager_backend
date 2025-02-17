from rest_framework import serializers

from .models import Balance


class BalanceSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Balance
        fields = [
            'id',
            'user',
            'name',
            'amount',
            'currency',
            'created_at',
        ]
        read_only_fields = ['created_at', 'user']
