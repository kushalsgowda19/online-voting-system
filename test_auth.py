import requests
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

# Get the user and generate a token
user = User.objects.get(username='admin2')
refresh = RefreshToken.for_user(user)
access_token = str(refresh.access_token)

# Test the endpoint
url = 'http://localhost:8000/api/auth/user/'
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

response = requests.get(url, headers=headers)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
