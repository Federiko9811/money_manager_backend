from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from balances.models import Balance
from transactions.models import IncomeOutcomeTransaction, TransferTransaction

User = get_user_model()


class TransactionsTests(TestCase):
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

        self.income_transaction = IncomeOutcomeTransaction.objects.create(
            user=self.user,
            name='Salary',
            amount=1000.00,
            date='2021-01-01',
            note='Monthly salary',
            currency='EUR',
            transaction_type='incoming',
            balance=self.balance1
        )

        self.outcome_transaction = IncomeOutcomeTransaction.objects.create(
            user=self.user,
            name='Rent',
            amount=500.00,
            date='2021-01-01',
            note='Monthly rent',
            currency='EUR',
            transaction_type='outgoing',
            balance=self.balance1
        )

        self.transfer_transaction = TransferTransaction.objects.create(
            user=self.user,
            name='Transfer',
            amount=200.00,
            date='2021-01-01',
            note='Monthly transfer',
            currency='EUR',
            balance_from=self.balance1,
            balance_to=self.balance2
        )

    def test_list_all_transactions(self):
        """Test listing all transactions via the API."""
        url = reverse('transaction-list')
        response = self.client.get(url, format='json')

        for transaction in response.data:
            print(transaction.get('detail_url'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_list_other_user_transactions(self):
        """Test listing other user's transactions via the API."""
        self.client.force_authenticate(user=self.other_user)
        url = reverse('transaction-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)