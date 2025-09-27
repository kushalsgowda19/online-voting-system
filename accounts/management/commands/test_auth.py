from django.core.management.base import BaseCommand
import requests
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

class Command(BaseCommand):
    help = 'Test the auth user endpoint'

    def handle(self, *args, **options):
        try:
            # Get the user and generate a token
            user = User.objects.get(username='admin2')
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            self.stdout.write(self.style.SUCCESS(f'Generated access token for {user.username}'))
            
            # Test the endpoint
            url = 'http://localhost:8000/api/auth/user/'
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            self.stdout.write('Testing endpoint: GET /api/auth/user/')
            response = requests.get(url, headers=headers)
            
            self.stdout.write(self.style.SUCCESS(f'Status Code: {response.status_code}'))
            self.stdout.write(f'Response: {response.text}')
            
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {str(e)}'))
