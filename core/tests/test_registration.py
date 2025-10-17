# core/tests/test_registration.py
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from ..models import Customer

class RegistrationTests(APITestCase):
    """
    Test suite for the user registration endpoint.
    """

    def test_successful_registration(self):
        """
        Ensure a new user and customer can be created successfully.
        """
        # Arrange: Define the data for a new user
        registration_data = {
            "username": "testuser",
            "password": "testpassword123",
            "full_name": "Test User Full Name",
            "email": "test@example.com",
            "phone_number": "555-0101",
            "date_of_birth": "1990-01-01",
            "gender": "O"
        }

        # Act: Make a POST request to the registration endpoint
        url = '/api/register/'
        response = self.client.post(url, registration_data, format='json')

        # Assert: Check the results
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')