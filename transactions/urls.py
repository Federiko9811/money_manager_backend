from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import IncomeOutcomeTransactionViewSet, TransferTransactionViewSet, BaseTransactionViewSet

router = DefaultRouter()
router.register(r'', BaseTransactionViewSet, basename='transaction')
router.register(r'income-outcome-transactions', IncomeOutcomeTransactionViewSet, basename='income_outcome_transaction')
router.register(r'transfer-transactions', TransferTransactionViewSet, basename='transfer_transaction')

urlpatterns = [
    path('', include((router.urls, 'transactions'), namespace='transactions')),
    # Include the router URLs with namespace
]
