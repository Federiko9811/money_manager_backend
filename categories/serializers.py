from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Display user as a string (e.g., username)

    class Meta:
        model = Category
        fields = [
            'id',
            'user',  # Read-only field
            'name',
            'created_at',
        ]
        read_only_fields = ['created_at', 'user']  # Ensure these fields are read-only

    def validate_name(self, value):
        """
        Ensure the category name is unique per user.
        """
        user = self.context['request'].user
        if Category.objects.filter(user=user, name=value).exists():
            raise serializers.ValidationError("A category with this name already exists for the user.")
        return value