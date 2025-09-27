import os
import django

def setup_django():
    """Set up Django environment."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voting_system_backend.settings')
    django.setup()

def list_users():
    """List all users in the database."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    print("\n=== Current Users ===")
    for user in User.objects.all():
        print(f"Username: {user.username}, Email: {user.email}, Is Staff: {user.is_staff}, Is Superuser: {user.is_superuser}")

def create_test_users():
    """Create test users if they don't exist."""
    from django.contrib.auth import get_user_model
    from accounts.models import UserProfile
    
    User = get_user_model()
    
    test_users = [
        {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'is_staff': False,
            'is_superuser': False,
            'role': 'voter'
        },
        {
            'username': 'voter1',
            'email': 'voter1@example.com',
            'password': 'voter123',
            'is_staff': False,
            'is_superuser': False,
            'role': 'voter'
        },
        {
            'username': 'admin2',
            'email': 'admin2@example.com',
            'password': 'admin123',
            'is_staff': True,
            'is_superuser': True,
            'role': 'admin'
        }
    ]
    
    for user_data in test_users:
        username = user_data.pop('username')
        password = user_data.pop('password')
        role = user_data.pop('role')
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults=user_data
        )
        
        if created:
            user.set_password(password)
            user.save()
            
            # Create user profile
            UserProfile.objects.create(user=user, role=role)
            print(f"Created user: {username} with role: {role}")
        else:
            print(f"User {username} already exists")

if __name__ == "__main__":
    setup_django()
    print("=== Listing current users ===")
    list_users()
    
    print("\n=== Creating test users ===")
    create_test_users()
    
    print("\n=== Updated user list ===")
    list_users()
