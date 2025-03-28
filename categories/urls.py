from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet

# Create a router and register the CategoryViewSet
router = DefaultRouter()
router.register(r'', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),  # Include the router URLs
]
