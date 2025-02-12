from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Balance

# Use the custom user model
User = get_user_model()


class BalanceViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def test_create_balance(self):
        """Test creating a balance via the API."""
        url = reverse('balance-list')  # Ensure this matches the router's name
        data = {
            'name': 'Savings Account',
            'amount': 1500.00,
            'currency': 'USD'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Balance.objects.count(), 1)
        balance = Balance.objects.first()
        self.assertEqual(balance.name, 'Savings Account')
        self.assertEqual(balance.amount, 1500.00)
        self.assertEqual(balance.currency, 'USD')

    def test_list_balances(self):
        """Test listing balances via the API."""
        Balance.objects.create(user=self.user, name="Savings Account", amount=1000.00, currency="USD")
        Balance.objects.create(user=self.user, name="Checking Account", amount=500.00, currency="EUR")

        url = reverse('balance-list')  # Ensure this matches the router's name
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_balance(self):
        """Test retrieving a specific balance via the API."""
        balance = Balance.objects.create(user=self.user, name="Savings Account", amount=1000.00, currency="USD")
        url = reverse('balance-detail', args=[balance.id])  # Ensure this matches the router's name
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Savings Account')

    def test_update_balance(self):
        """Test updating a balance via the API."""
        balance = Balance.objects.create(user=self.user, name="Savings Account", amount=1000.00, currency="USD")
        url = reverse('balance-detail', args=[balance.id])  # Ensure this matches the router's name
        updated_data = {
            'name': 'Updated Savings Account',
            'amount': 2000.00,
            'currency': 'EUR'
        }
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        balance.refresh_from_db()
        self.assertEqual(balance.name, 'Updated Savings Account')
        self.assertEqual(balance.amount, 2000.00)
        self.assertEqual(balance.currency, 'EUR')

    def test_delete_balance(self):
        """Test deleting a balance via the API."""
        balance = Balance.objects.create(user=self.user, name="Savings Account", amount=1000.00, currency="USD")
        url = reverse('balance-detail', args=[balance.id])  # Ensure this matches the router's name
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Balance.objects.count(), 0)

    def test_create_balance_with_invalid_currency(self):
        """Test creating a balance with an invalid currency."""
        url = reverse('balance-list')  # Ensure this matches the router's name
        data = {
            'name': 'Invalid Currency Account',
            'amount': 1500.00,
            'currency': 'XYZ'  # Invalid currency
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('currency', response.data)
