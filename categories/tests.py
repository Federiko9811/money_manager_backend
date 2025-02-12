from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Category
from .serializers import CategorySerializer

# Use the custom user model
User = get_user_model()

class CategoryModelTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_create_category(self):
        """Test creating a category instance."""
        category = Category.objects.create(
            user=self.user,
            name="Groceries"
        )
        self.assertEqual(str(category), "testuser - Groceries")
        self.assertEqual(Category.objects.count(), 1)

    def test_category_unique_per_user(self):
        """Test that category names are unique per user."""
        Category.objects.create(user=self.user, name="Groceries")
        with self.assertRaises(Exception):  # Attempting to create a duplicate should raise an exception
            Category.objects.create(user=self.user, name="Groceries")


class CategorySerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.category_data = {
            'name': 'Utilities'
        }

    def test_serializer_valid_data(self):
        """Test that the serializer works with valid data."""
        serializer = CategorySerializer(data=self.category_data, context={'request': self._get_mock_request()})
        self.assertTrue(serializer.is_valid())

    def test_serializer_invalid_data_duplicate_name(self):
        """Test that the serializer fails with a duplicate category name for the same user."""
        Category.objects.create(user=self.user, name="Utilities")
        serializer = CategorySerializer(data=self.category_data, context={'request': self._get_mock_request()})
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def _get_mock_request(self):
        """Helper method to create a mock request object."""
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = self.user
        return request


class CategoryViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def test_create_category(self):
        """Test creating a category via the API."""
        url = reverse('category-list')  # 'category-list' is the name of the ModelViewSet endpoint
        data = {
            'name': 'Groceries'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 1)
        category = Category.objects.first()
        self.assertEqual(category.name, 'Groceries')
        self.assertEqual(category.user, self.user)

    def test_create_category_duplicate_name(self):
        """Test creating a category with a duplicate name for the same user."""
        Category.objects.create(user=self.user, name="Groceries")
        url = reverse('category-list')
        data = {
            'name': 'Groceries'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_list_categories(self):
        """Test listing categories via the API."""
        Category.objects.create(user=self.user, name="Groceries")
        Category.objects.create(user=self.user, name="Utilities")

        url = reverse('category-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_category(self):
        """Test retrieving a specific category via the API."""
        category = Category.objects.create(user=self.user, name="Groceries")
        url = reverse('category-detail', args=[category.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Groceries')

    def test_update_category(self):
        """Test updating a category via the API."""
        category = Category.objects.create(user=self.user, name="Groceries")
        url = reverse('category-detail', args=[category.id])
        updated_data = {
            'name': 'Food'
        }
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        category.refresh_from_db()
        self.assertEqual(category.name, 'Food')

    def test_delete_category(self):
        """Test deleting a category via the API."""
        category = Category.objects.create(user=self.user, name="Groceries")
        url = reverse('category-detail', args=[category.id])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 0)