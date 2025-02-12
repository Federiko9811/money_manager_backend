from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from balances.models import Balance
from categories.models import Category
from .models import Transaction
from .serializers import TransactionSerializer

# Use the custom user model
User = get_user_model()


class TransactionModelTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        # Create balances for the user
        self.balance1 = Balance.objects.create(user=self.user, name="Savings Account", amount=1000.00, currency="EUR")
        self.balance2 = Balance.objects.create(user=self.user, name="Checking Account", amount=500.00, currency="USD")

        # Create a category
        self.category = Category.objects.create(user=self.user, name="Groceries")

    def test_create_transaction(self):
        """Test creating a transaction instance."""
        transaction = Transaction.objects.create(
            user=self.user,
            balance_from=self.balance1,
            name="Groceries",
            amount=50.00,
            transaction_type="outgoing",
            date="2023-10-10T10:00:00Z",
            currency="EUR"
        )
        self.assertEqual(str(transaction), "testuser - Groceries (outgoing - EUR)")
        self.assertEqual(Transaction.objects.count(), 1)

    def test_transfer_transaction(self):
        """Test creating a transfer transaction."""
        transaction = Transaction.objects.create(
            user=self.user,
            balance_from=self.balance1,
            balance_to=self.balance2,
            name="Transfer to Checking",
            amount=200.00,
            transaction_type="transfer",
            date="2023-10-10T10:00:00Z",
            currency="EUR"
        )
        self.assertEqual(str(transaction), "testuser - Transfer to Checking (transfer - EUR)")
        self.assertEqual(Transaction.objects.count(), 1)

    def test_invalid_transfer_same_balance(self):
        """Test that a transfer cannot have the same source and destination balance."""
        with self.assertRaises(Exception):  # Attempting to create such a transaction should raise an exception
            Transaction.objects.create(
                user=self.user,
                balance_from=self.balance1,
                balance_to=self.balance1,
                name="Invalid Transfer",
                amount=200.00,
                transaction_type="transfer",
                date="2023-10-10T10:00:00Z",
                currency="EUR"
            )


class TransactionSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.balance1 = Balance.objects.create(user=self.user, name="Savings Account", amount=1000.00, currency="EUR")
        self.balance2 = Balance.objects.create(user=self.user, name="Checking Account", amount=500.00, currency="USD")
        self.category = Category.objects.create(user=self.user, name="Groceries")

        self.transaction_data = {
            'balance_from': self.balance1.id,
            'name': 'Groceries',
            'amount': 50.00,
            'transaction_type': 'outgoing',
            'date': '2023-10-10T10:00:00Z',
            'currency': 'EUR'
        }

    def test_serializer_valid_data(self):
        """Test that the serializer works with valid data."""
        data = {
            'balance_from': self.balance1.id,
            'balance_to': self.balance2.id,  # Include balance_to for a valid transfer
            'category': self.category.id,  # Include a valid category
            'name': 'Valid Transfer',
            'amount': 200.00,
            'transaction_type': 'transfer',
            'date': '2023-10-10T10:00:00Z',
            'currency': 'EUR'
        }
        serializer = TransactionSerializer(data=data, context={'request': self._get_mock_request()})
        self.assertTrue(serializer.is_valid())  # Ensure the serializer validates successfully

    def test_serializer_invalid_transfer_same_balance(self):
        """Test that the serializer fails for a transfer with the same source and destination balance."""
        invalid_data = {
            'balance_from': self.balance1.id,
            'balance_to': self.balance1.id,  # Same balance for source and destination
            'category': self.category.id,  # Include a valid category
            'name': 'Invalid Transfer',
            'amount': 200.00,
            'transaction_type': 'transfer',
            'date': '2023-10-10T10:00:00Z',
            'currency': 'EUR'
        }
        serializer = TransactionSerializer(data=invalid_data, context={'request': self._get_mock_request()})
        self.assertFalse(serializer.is_valid())  # Ensure the serializer fails validation
        self.assertIn('non_field_errors', serializer.errors)  # Check for custom validation error

    def _get_mock_request(self):
        """Helper method to create a mock request object."""
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = self.user
        return request


class TransactionViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

        # Create balances for the user
        self.balance1 = Balance.objects.create(user=self.user, name="Savings Account", amount=1000.00, currency="EUR")
        self.balance2 = Balance.objects.create(user=self.user, name="Checking Account", amount=500.00, currency="USD")

        # Create a category
        self.category = Category.objects.create(user=self.user, name="Groceries")

    def test_create_transaction(self):
        """Test creating a transaction via the API."""
        url = reverse('transaction-list')  # 'transaction-list' is the name of the ModelViewSet endpoint
        data = {
            'balance_from': self.balance1.id,
            'category': self.category.id,  # Include a valid category
            'name': 'Groceries',
            'amount': 50.00,
            'transaction_type': 'outgoing',
            'date': '2023-10-10T10:00:00Z',
            'currency': 'EUR'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 1)
        transaction = Transaction.objects.first()
        self.assertEqual(transaction.name, 'Groceries')
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.category, self.category)  # Verify the category is set correctly

    def test_create_invalid_transfer_same_balance(self):
        """Test creating a transfer transaction with the same source and destination balance."""
        url = reverse('transaction-list')
        data = {
            'balance_from': self.balance1.id,
            'balance_to': self.balance1.id,
            'category': self.category.id,
            'name': 'Invalid Transfer',
            'amount': 200.00,
            'transaction_type': 'transfer',
            'date': '2023-10-10T10:00:00Z',
            'currency': 'EUR'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_list_transactions(self):
        """Test listing transactions via the API."""
        Transaction.objects.create(
            user=self.user,
            balance_from=self.balance1,
            name="Groceries",
            amount=50.00,
            transaction_type="outgoing",
            date="2023-10-10T10:00:00Z",
            currency="EUR"
        )
        Transaction.objects.create(
            user=self.user,
            balance_from=None,
            balance_to=self.balance2,
            name="Salary",
            amount=2000.00,
            transaction_type="incoming",
            date="2023-10-01T08:00:00Z",
            currency="EUR"
        )

        url = reverse('transaction-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_transaction(self):
        """Test retrieving a specific transaction via the API."""
        transaction = Transaction.objects.create(
            user=self.user,
            balance_from=self.balance1,
            name="Groceries",
            amount=50.00,
            transaction_type="outgoing",
            date="2023-10-10T10:00:00Z",
            currency="EUR"
        )
        url = reverse('transaction-detail', args=[transaction.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Groceries')

    def test_update_transaction(self):
        """Test updating a transaction via the API."""
        transaction = Transaction.objects.create(
            user=self.user,
            balance_from=self.balance1,
            name="Groceries",
            amount=50.00,
            transaction_type="outgoing",
            date="2023-10-10T10:00:00Z",
            currency="EUR"
        )
        url = reverse('transaction-detail', args=[transaction.id])
        updated_data = {
            'name': 'Food',
            'amount': 75.00,
            'note': 'Updated note'
        }
        response = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        transaction.refresh_from_db()
        self.assertEqual(transaction.name, 'Food')
        self.assertEqual(transaction.amount, 75.00)
        self.assertEqual(transaction.note, 'Updated note')

    def test_delete_transaction(self):
        """Test deleting a transaction via the API."""
        transaction = Transaction.objects.create(
            user=self.user,
            balance_from=self.balance1,
            name="Groceries",
            amount=50.00,
            transaction_type="outgoing",
            date="2023-10-10T10:00:00Z",
            currency="EUR"
        )
        url = reverse('transaction-detail', args=[transaction.id])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Transaction.objects.count(), 0)
