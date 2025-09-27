from django.core.management.base import BaseCommand
from django.test import RequestFactory
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.views import UserDetailsView

class Command(BaseCommand):
    help = 'Test the auth user endpoint'

    def handle(self, *args, **options):
        try:
            # Get the admin2 user
            user = User.objects.get(username='admin2')
            self.stdout.write(self.style.SUCCESS(f'Found user: {user.username}'))
            
            # Create a token for the user
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            self.stdout.write(self.style.SUCCESS('Generated access token'))
            
            # Create a request with the token
            factory = RequestFactory()
            request = factory.get('/api/auth/user/')
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
            
            # Call the view directly
            view = UserDetailsView.as_view()
            response = view(request)
            
            self.stdout.write(self.style.SUCCESS(f'Status Code: {response.status_code}'))
            self.stdout.write(f'Response: {response.data}')
            
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {str(e)}'))
