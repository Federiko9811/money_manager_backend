from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from balances.models import Balance
from categories.models import Category
from .models import Transaction

# Use the custom user model
User = get_user_model()


class TransactionPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create two users: one for the owner and one for an unauthorized user
        self.owner = User.objects.create_user(username='owner', password='ownerpassword')
        self.unauthorized_user = User.objects.create_user(username='unauthorized', password='unauthorizedpassword')

        # Create balances for the owner
        self.owner_balance1 = Balance.objects.create(user=self.owner, name="Owner Savings", amount=1000.00,
                                                     currency="EUR")
        self.owner_balance2 = Balance.objects.create(user=self.owner, name="Owner Checking", amount=500.00,
                                                     currency="USD")

        # Create a category for the owner
        self.owner_category = Category.objects.create(user=self.owner, name="Owner Groceries")

        # Create a transaction owned by the owner
        self.owner_transaction = Transaction.objects.create(
            user=self.owner,
            balance_from=self.owner_balance1,
            category=self.owner_category,
            name="Owner Transaction",
            amount=50.00,
            transaction_type="outgoing",
            date="2023-10-10T10:00:00Z",
            currency="EUR"
        )

    def authenticate_client(self, user):
        """Helper method to authenticate the client with a specific user."""
        self.client.force_authenticate(user=user)

    def test_unauthorized_user_cannot_list_transactions(self):
        """Test that an unauthorized user cannot list another user's transactions."""
        self.authenticate_client(self.unauthorized_user)
        url = reverse('transaction-list')
        response = self.client.get(url, format='json')

        # The unauthorized user should only see their own transactions (none in this case)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_unauthorized_user_cannot_retrieve_transaction(self):
        """Test that an unauthorized user cannot retrieve another user's transaction."""
        self.authenticate_client(self.unauthorized_user)
        url = reverse('transaction-detail', args=[self.owner_transaction.id])
        response = self.client.get(url, format='json')

        # The unauthorized user should not find the transaction (404 Not Found)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_user_cannot_update_transaction(self):
        """Test that an unauthorized user cannot update another user's transaction."""
        self.authenticate_client(self.unauthorized_user)
        url = reverse('transaction-detail', args=[self.owner_transaction.id])
        updated_data = {
            'name': 'Unauthorized Update',
            'amount': 75.00,
            'note': 'Unauthorized note'
        }
        response = self.client.patch(url, updated_data, format='json')

        # The unauthorized user should not be allowed to update the transaction (404 Not Found)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_user_cannot_delete_transaction(self):
        """Test that an unauthorized user cannot delete another user's transaction."""
        self.authenticate_client(self.unauthorized_user)
        url = reverse('transaction-detail', args=[self.owner_transaction.id])
        response = self.client.delete(url, format='json')

        # The unauthorized user should not be allowed to delete the transaction (404 Not Found)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_can_list_own_transactions(self):
        """Test that the owner can list their own transactions."""
        self.authenticate_client(self.owner)
        url = reverse('transaction-list')
        response = self.client.get(url, format='json')

        # The owner should see their own transactions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only the owner's transaction should be listed

    def test_owner_can_retrieve_own_transaction(self):
        """Test that the owner can retrieve their own transaction."""
        self.authenticate_client(self.owner)
        url = reverse('transaction-detail', args=[self.owner_transaction.id])
        response = self.client.get(url, format='json')

        # The owner should be able to retrieve their own transaction
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Owner Transaction')

    def test_owner_can_update_own_transaction(self):
        """Test that the owner can update their own transaction."""
        self.authenticate_client(self.owner)
        url = reverse('transaction-detail', args=[self.owner_transaction.id])
        updated_data = {
            'name': 'Updated Name',
            'amount': 75.00,
            'note': 'Updated note'
        }
        response = self.client.patch(url, updated_data, format='json')

        # The owner should be able to update their own transaction
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.owner_transaction.refresh_from_db()
        self.assertEqual(self.owner_transaction.name, 'Updated Name')
        self.assertEqual(self.owner_transaction.amount, 75.00)
        self.assertEqual(self.owner_transaction.note, 'Updated note')

    def test_owner_can_delete_own_transaction(self):
        """Test that the owner can delete their own transaction."""
        self.authenticate_client(self.owner)
        url = reverse('transaction-detail', args=[self.owner_transaction.id])
        response = self.client.delete(url, format='json')

        # The owner should be able to delete their own transaction
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Transaction.objects.count(), 0)
