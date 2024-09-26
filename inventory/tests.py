from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Item
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

User = get_user_model()

class UserAuthTests(APITestCase):

    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "test_password"
        }
        
    def test_user_registration(self):
        """Test user registration with valid data."""
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')

    def test_user_registration_with_existing_email(self):
        """Test registration with an existing email."""
        self.client.post(self.register_url, self.user_data, format='json')
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)


    def test_user_login(self):
        """Test user login with valid credentials."""
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {
            "email": "testuser@example.com",
            "password": "test_password"
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_user_login_with_invalid_credentials(self):
        """Test login with invalid credentials."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "test_password"
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ItemAPITest(APITestCase):
    def setUp(self):
        self.items_url = reverse('item-list-create')
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # item data for tests
        self.item_data = {
            'name': 'Test Item',
            'description': 'A description of the test item',
            'price': 100.0,
        }

    def test_create_item(self):
        response = self.client.post(self.items_url, self.item_data, format='json')
        
        # Assert that the first creation was successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)

        # Attempt to create the same item again
        duplicate_response = self.client.post(self.items_url, self.item_data, format='json')

        # Assert that trying to create a duplicate item returns a 400 error
        self.assertEqual(duplicate_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', duplicate_response.data)
        self.assertEqual(duplicate_response.data['name'], ['item with this name already exists.'])

    def test_get_item(self):
        create_response = self.client.post(self.items_url, self.item_data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        item_id = create_response.data['id']

        # Retrieve the item
        response = self.client.get(reverse('item-detail', kwargs={'pk': item_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], item_id)

    def test_delete_item(self):
        create_response = self.client.post(self.items_url, self.item_data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        item_id = create_response.data['id']

        # Delete the item
        delete_response = self.client.delete(reverse('item-detail', kwargs={'pk': item_id}))
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        # Attempt to retrieve the deleted item to confirm it's gone
        retrieve_response = self.client.get(reverse('item-detail', kwargs={'pk': item_id}))
        self.assertEqual(retrieve_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_item_missing_fields(self):
        # Attempt to create an item without a required field
        invalid_item_data = {
            'description': 'Missing name',
            'price': 100.0,
        }
        response = self.client.post(self.items_url, invalid_item_data, format='json')
        
        # Assert that the creation fails
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_update_item(self):
        create_response = self.client.post(self.items_url, self.item_data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        item_id = create_response.data['id']

        # Update item data
        updated_item_data = {
            'name': 'Updated Test Item',
            'description': 'An updated description',
            'price': 150.0,
        }

        # Perform the update
        update_response = self.client.put(reverse('item-detail', kwargs={'pk': item_id}), updated_item_data, format='json')
        
        # Assert the update was successful
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['name'], updated_item_data['name'])
        self.assertEqual(update_response.data['description'], updated_item_data['description'])
        self.assertEqual(update_response.data['price'], '150.00')  # Expect as '150.00'

        # Retrieve the updated item to confirm changes
        retrieve_response = self.client.get(reverse('item-detail', kwargs={'pk': item_id}))
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieve_response.data['name'], updated_item_data['name'])