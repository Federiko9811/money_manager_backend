from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import BalanceViewSet

# Create a router and register the BalanceViewSet
router = DefaultRouter()
router.register(r'', BalanceViewSet, basename='balance')

urlpatterns = [
    path('', include(router.urls)),  # Include the router URLs
]
