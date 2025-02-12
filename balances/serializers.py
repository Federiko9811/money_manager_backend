from rest_framework import serializers

from .models import Balance


class BalanceSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Display user as a string (e.g., username)

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
        read_only_fields = ['created_at', 'user']  # Ensure these fields are read-only
