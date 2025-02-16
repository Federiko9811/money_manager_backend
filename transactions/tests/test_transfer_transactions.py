from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from balances.models import Balance
from transactions.models import TransferTransaction
from transactions.serializers import TransferTransactionSerializer

User = get_user_model()


class TransferTransactionTests(TestCase):
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

    def test_list_all_transfer_transactions(self):
        """Test listing all transfer transactions via the API."""
        TransferTransaction.objects.create(
            user=self.user,
            name='Transfer',
            amount=100.00,
            date='2021-01-01',
            note='Transfer to checking account',
            currency='EUR',
            balance_from=self.balance1,
            balance_to=self.balance2
        )

        response = self.client.get(reverse('transfer_transaction-list'))
        transactions = TransferTransaction.objects.all()
        serializer = TransferTransactionSerializer(transactions, many=True)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_transfer_transaction(self):
        """Test creating a new transfer transaction via the API."""
        data = {
            'name': 'Transfer',
            'amount': 100.00,
            'date': '2021-01-01',
            'note': 'Transfer to checking account',
            'currency': 'EUR',
            'balance_from': self.balance1.id,
            'balance_to': self.balance2.id
        }

        response = self.client.post(reverse('transfer_transaction-list'), data)
        transaction = TransferTransaction.objects.get(name='Transfer')
        serializer = TransferTransactionSerializer(transaction)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_transfer_transaction_same_balance(self):
        """Test creating a new transfer transaction with the same source and destination balance."""
        data = {
            'name': 'Transfer',
            'amount': 100.00,
            'date': '2021-01-01',
            'note': 'Transfer to checking account',
            'currency': 'EUR',
            'balance_from': self.balance1.id,
            'balance_to': self.balance1.id
        }

        response = self.client.post(reverse('transfer_transaction-list'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_transfer_transaction(self):
        """Test retrieving a specific transfer transaction via the API."""
        transaction = TransferTransaction.objects.create(
            user=self.user,
            name='Transfer',
            amount=100.00,
            date='2021-01-01',
            note='Transfer to checking account',
            currency='EUR',
            balance_from=self.balance1,
            balance_to=self.balance2
        )

        response = self.client.get(reverse('transfer_transaction-detail', args=[transaction.id]))
        serializer = TransferTransactionSerializer(transaction)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_not_owned_transfer_transaction(self):
        """Test retrieving a transaction that does not belong to the authenticated user."""
        transaction = TransferTransaction.objects.create(
            user=self.other_user,
            name='Transfer',
            amount=100.00,
            date='2021-01-01',
            note='Transfer to checking account',
            currency='EUR',
            balance_from=self.balance1,
            balance_to=self.balance2
        )

        response = self.client.get(reverse('transfer_transaction-detail', args=[transaction.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_transfer_transaction(self):
        """Test updating an existing transfer transaction via the API."""
        transaction = TransferTransaction.objects.create(
            user=self.user,
            name='Transfer',
            amount=100.00,
            date='2021-01-01',
            note='Transfer to checking account',
            currency='EUR',
            balance_from=self.balance1,
            balance_to=self.balance2
        )

        data = {
            'name': 'Updated Transfer',
            'amount': 200.00,
            'date': '2021-01-02',
            'note': 'Updated transfer to checking account',
            'currency': 'USD',
            'balance_from': self.balance2.id,
            'balance_to': self.balance1.id
        }

        response = self.client.put(reverse('transfer_transaction-detail', args=[transaction.id]), data)
        transaction.refresh_from_db()
        serializer = TransferTransactionSerializer(transaction)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_transfer_transaction_same_balance(self):
        """Test updating a transfer transaction with the same source and destination balance."""
        transaction = TransferTransaction.objects.create(
            user=self.user,
            name='Transfer',
            amount=100.00,
            date='2021-01-01',
            note='Transfer to checking account',
            currency='EUR',
            balance_from=self.balance1,
            balance_to=self.balance2
        )

        data = {
            'name': 'Updated Transfer',
            'amount': 200.00,
            'date': '2021-01-02',
            'note': 'Updated transfer to checking account',
            'currency': 'USD',
            'balance_from': self.balance1.id,
            'balance_to': self.balance1.id
        }

        response = self.client.put(reverse('transfer_transaction-detail', args=[transaction.id]), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_not_owned_transfer_transaction(self):
        """Test updating a transaction that does not belong to the authenticated user."""
        transaction = TransferTransaction.objects.create(
            user=self.other_user,
            name='Transfer',
            amount=100.00,
            date='2021-01-01',
            note='Transfer to checking account',
            currency='EUR',
            balance_from=self.balance1,
            balance_to=self.balance2
        )

        data = {
            'name': 'Updated Transfer',
            'amount': 200.00,
            'date': '2021-01-02',
            'note': 'Updated transfer to checking account',
            'currency': 'USD',
            'balance_from': self.balance2.id,
            'balance_to': self.balance1.id
        }

        response = self.client.put(reverse('transfer_transaction-detail', args=[transaction.id]), data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_transfer_transaction(self):
        """Test deleting an existing transfer transaction via the API."""
        transaction = TransferTransaction.objects.create(
            user=self.user,
            name='Transfer',
            amount=100.00,
            date='2021-01-01',
            note='Transfer to checking account',
            currency='EUR',
            balance_from=self.balance1,
            balance_to=self.balance2
        )

        response = self.client.delete(reverse('transfer_transaction-detail', args=[transaction.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TransferTransaction.objects.count(), 0)

    def test_delete_not_owned_transfer_transaction(self):
        """Test deleting a transaction that does not belong to the authenticated user."""
        transaction = TransferTransaction.objects.create(
            user=self.other_user,
            name='Transfer',
            amount=100.00,
            date='2021-01-01',
            note='Transfer to checking account',
            currency='EUR',
            balance_from=self.balance1,
            balance_to=self.balance2
        )

        response = self.client.delete(reverse('transfer_transaction-detail', args=[transaction.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
