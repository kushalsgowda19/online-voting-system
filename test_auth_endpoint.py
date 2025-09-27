import os
import sys
import django

# Add the project directory to the Python path
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voting_system_backend.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

def test_auth_endpoint():
    # Get the admin2 user
    user = User.objects.get(username='admin2')
    
    # Create a token for the user
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    # Set up the test client
    client = Client(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    # Test the endpoint
    response = client.get('/api/auth/user/')
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Content: {response.content.decode('utf-8')}")

if __name__ == "__main__":
    test_auth_endpoint()
