from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Transaction
from .serializers import TransactionSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access this endpoint

    def get_queryset(self):
        # Return only the transactions belonging to the authenticated user
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically associate the transaction with the authenticated user
        serializer.save(user=self.request.user)
