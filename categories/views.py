from rest_framework import viewsets

from utils.permissions import IsOwner
from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        # Return only the categories belonging to the authenticated user
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically associate the category with the authenticated user
        serializer.save(user=self.request.user)
