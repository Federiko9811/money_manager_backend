from rest_framework import mixins, viewsets

from utils.permissions import IsOwner
from .models import IncomeOutcomeTransaction, TransferTransaction, BaseTransaction
from .serializers.base_transaction_serializers import BaseTransactionSerializer
from .serializers.income_outcome_transaction_serializers import IncomeOutcomeTransactionSerializer, \
    CreateIncomeOutcomeTransactionSerializer
from .serializers.transfer_transaction_serializers import TransferTransactionSerializer


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
    permission_classes = [IsOwner]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateIncomeOutcomeTransactionSerializer
        return IncomeOutcomeTransactionSerializer

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
