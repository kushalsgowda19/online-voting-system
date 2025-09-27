import os
import django
import requests

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voting_system_backend.settings')
django.setup()

# Now import Django models after setup
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

# Get the admin2 user
user = User.objects.get(username='admin2')

# Create a token for the user
refresh = RefreshToken.for_user(user)
access_token = str(refresh.access_token)

# Set up the request
url = 'http://localhost:8000/api/auth/user/'
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

# Make the request
response = requests.get(url, headers=headers)

# Print the results
print(f"Request URL: {url}")
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

# Also try with a trailing slash
url_with_slash = 'http://localhost:8000/api/auth/user/'
response_with_slash = requests.get(url_with_slash, headers=headers)

print("\nTrying with trailing slash:")
print(f"Request URL: {url_with_slash}")
print(f"Status Code: {response_with_slash.status_code}")
print(f"Response: {response_with_slash.text}")
