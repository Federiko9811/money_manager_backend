from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from balances.models import Balance
from transactions.models import IncomeOutcomeTransaction
from transactions.serializers import IncomeOutcomeTransactionSerializer

User = get_user_model()


class IncomeOutcomeTransactionsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.other_user = User.objects.create_user(username='otheruser', password='otherpassword')
        self.client.force_authenticate(user=self.user)

        self.balance1 = Balance.objects.create(
            user=self.user,
            name='Savings Account',
            amount=1000.00,
            currency='USD'
        )

        self.balance2 = Balance.objects.create(
            user=self.user,
            name='Checking Account',
            amount=500.00,
            currency='EUR'
        )

    def test_list_all_income_outcome_transactions(self):
        """Test listing all income/outcome transactions via the API."""
        IncomeOutcomeTransaction.objects.create(
            user=self.user,
            name='Salary',
            amount=1000.00,
            date='2021-01-01',
            note='Monthly salary',
            currency='EUR',
            transaction_type='income',
            balance=self.balance1
        )

        IncomeOutcomeTransaction.objects.create(
            user=self.user,
            name='Rent',
            amount=500.00,
            date='2021-01-01',
            note='Monthly rent',
            currency='EUR',
            transaction_type='outcome',
            balance=self.balance1
        )

        IncomeOutcomeTransaction.objects.create(
            user=self.user,
            name='Rent',
            amount=500.00,
            date='2021-01-01',
            note='Monthly rent',
            currency='EUR',
            transaction_type='outcome',
            balance=self.balance1
        )

        url = reverse('income_outcome_transaction-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        expected_data = IncomeOutcomeTransactionSerializer(IncomeOutcomeTransaction.objects.all(), many=True).data
        self.assertListEqual(response.data, expected_data)

    def test_retrieve_income_outcome_transaction(self):
        """Test retrieving a specific income/outcome transaction via the API."""
        income_transaction = IncomeOutcomeTransaction.objects.create(
            user=self.user,
            name='Salary',
            amount=1000.00,
            date='2021-01-01',
            note='Monthly salary',
            currency='EUR',
            transaction_type='income',
            balance=self.balance1
        )

        url = reverse('income_outcome_transaction-detail', args=[income_transaction.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = IncomeOutcomeTransactionSerializer(income_transaction).data
        self.assertDictEqual(response.data, expected_data)

    def test_retrieve_not_owned_income_outcome_transaction(self):
        """Test retrieving a transaction that does not belong to the authenticated user."""
        income_transaction = IncomeOutcomeTransaction.objects.create(
            user=self.other_user,
            name='Salary',
            amount=1000.00,
            date='2021-01-01',
            note='Monthly salary',
            currency='EUR',
            transaction_type='income',
            balance=self.balance1
        )

        url = reverse('income_outcome_transaction-detail', args=[income_transaction.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_income_outcome_transaction(self):
        """Test creating an income/outcome transaction via the API."""
        data = {
            'name': 'Salary',
            'amount': 1000.00,
            'date': '2021-01-01',
            'note': 'Monthly salary',
            'currency': 'EUR',
            'transaction_type': 'income',
            'balance': self.balance1.id
        }

        url = reverse('income_outcome_transaction-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(IncomeOutcomeTransaction.objects.count(), 1)
        income_transaction = IncomeOutcomeTransaction.objects.first()
        expected_data = IncomeOutcomeTransactionSerializer(income_transaction).data
        self.assertDictEqual(response.data, expected_data)

    def test_create_income_outcome_transaction_with_invalid_balance(self):
        """Test creating an income/outcome transaction with an invalid balance."""
        data = {
            'name': 'Salary',
            'amount': 1000.00,
            'date': '2021-01-01',
            'note': 'Monthly salary',
            'currency': 'EUR',
            'transaction_type': 'income',
            'balance': -1
        }

        url = reverse('income_outcome_transaction-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(IncomeOutcomeTransaction.objects.count(), 0)

    def test_update_income_outcome_transaction(self):
        """Test updating an income/outcome transaction via the API."""
        income_transaction = IncomeOutcomeTransaction.objects.create(
            user=self.user,
            name='Salary',
            amount=1000.00,
            date='2021-01-01',
            note='Monthly salary',
            currency='EUR',
            transaction_type='income',
            balance=self.balance1
        )

        url = reverse('income_outcome_transaction-detail', args=[income_transaction.id])
        updated_data = {
            'name': 'Updated Salary',
            'amount': 1500.00,
            'date': '2021-01-01',
            'note': 'Monthly salary',
            'currency': 'USD',
            'transaction_type': 'income',
            'balance': self.balance2.id
        }

        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        income_transaction.refresh_from_db()
        expected_data = IncomeOutcomeTransactionSerializer(income_transaction).data
        self.assertDictEqual(response.data, expected_data)

    def test_delete_income_outcome_transaction(self):
        """Test deleting an income/outcome transaction via the API."""
        income_transaction = IncomeOutcomeTransaction.objects.create(
            user=self.user,
            name='Salary',
            amount=1000.00,
            date='2021-01-01',
            note='Monthly salary',
            currency='EUR',
            transaction_type='income',
            balance=self.balance1
        )

        url = reverse('income_outcome_transaction-detail', args=[income_transaction.id])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(IncomeOutcomeTransaction.objects.count(), 0)

    def test_delete_not_owned_income_outcome_transaction(self):
        """Test deleting a transaction that does not belong to the authenticated user."""
        income_transaction = IncomeOutcomeTransaction.objects.create(
            user=self.other_user,
            name='Salary',
            amount=1000.00,
            date='2021-01-01',
            note='Monthly salary',
            currency='EUR',
            transaction_type='income',
            balance=self.balance1
        )

        url = reverse('income_outcome_transaction-detail', args=[income_transaction.id])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(IncomeOutcomeTransaction.objects.count(), 1)

    def test_create_income_outcome_transaction_with_invalid_currency(self):
        """Test creating an income/outcome transaction with an invalid currency."""
        data = {
            'name': 'Salary',
            'amount': 1000.00,
            'date': '2021-01-01',
            'note': 'Monthly salary',
            'currency': 'INVALID',
            'transaction_type': 'income',
            'balance': self.balance1.id
        }

        url = reverse('income_outcome_transaction-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(IncomeOutcomeTransaction.objects.count(), 0)

    def test_create_income_outcome_transaction_with_invalid_transaction_type(self):
        """Test creating an income/outcome transaction with an invalid transaction type."""
        data = {
            'name': 'Salary',
            'amount': 1000.00,
            'date': '2021-01-01',
            'note': 'Monthly salary',
            'currency': 'EUR',
            'transaction_type': 'INVALID',
            'balance': self.balance1.id
        }

        url = reverse('income_outcome_transaction-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(IncomeOutcomeTransaction.objects.count(), 0)
