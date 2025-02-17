from rest_framework import mixins, viewsets

from utils.permissions import IsOwner
from .models import IncomeOutcomeTransaction, TransferTransaction, BaseTransaction
from .serializers import IncomeOutcomeTransactionSerializer, TransferTransactionSerializer, BaseTransactionSerializer


class BaseTransactionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Base view set for all transaction types."""
    queryset = BaseTransaction.objects.all()
    serializer_class = BaseTransactionSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return BaseTransaction.objects.filter(user=self.request.user)


class IncomeOutcomeTransactionViewSet(viewsets.ModelViewSet):
    """View set for income and outcome transactions."""
    queryset = IncomeOutcomeTransaction.objects.all()
    serializer_class = IncomeOutcomeTransactionSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return IncomeOutcomeTransaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TransferTransactionViewSet(viewsets.ModelViewSet):
    """View set for transfer transactions."""
    queryset = TransferTransaction.objects.all()
    serializer_class = TransferTransactionSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return TransferTransaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
