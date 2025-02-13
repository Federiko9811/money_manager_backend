from rest_framework import viewsets

from utils.permissions import IsOwner
from .models import Balance
from .serializers import BalanceSerializer


class BalanceViewSet(viewsets.ModelViewSet):
    serializer_class = BalanceSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        # Return only the balances belonging to the authenticated user
        return Balance.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically associate the balance with the authenticated user
        serializer.save(user=self.request.user)
