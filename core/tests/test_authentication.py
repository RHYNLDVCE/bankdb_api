from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

class AuthenticationTests(APITestCase):
    """
    Test suite for authentication and permissions.
    """

    def setUp(self):
        """
        Create a test user that runs before each test.
        """
        self.user = User.objects.create_user(
            username='authtestuser', 
            password='testpassword123'
        )
        self.customer_url = '/api/customers/'

    def test_get_auth_token_successfully(self):
        """
        Ensure a user can get an auth token with correct credentials.
        """
        # Arrange
        url = '/api/get-token/'
        data = {'username': 'authtestuser', 'password': 'testpassword123'}

        # Act
        response = self.client.post(url, data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)
        self.assertEqual(Token.objects.count(), 1)
        self.assertEqual(Token.objects.get().user, self.user)

    def test_access_protected_endpoint_unauthorized(self):
        """
        Ensure unauthenticated users are denied access.
        """
        # Act
        response = self.client.get(self.customer_url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_protected_endpoint_authorized(self):
        """
        Ensure an authenticated user can access protected endpoints.
        """
        # Arrange: Get the token for our user
        token = Token.objects.create(user=self.user)
        # This is the key DRF testing method for authentication
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        # Act
        response = self.client.get(self.customer_url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)