from rest_framework import generics, permissions, status
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated
from elections.models import UserProfile
from .serializers import RegisterSerializer
from rest_framework.exceptions import PermissionDenied

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Return success response with user data
        return Response({
            'success': True,
            'message': 'Registration successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }, status=status.HTTP_201_CREATED)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

class UserDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'role': 'admin' if user.is_superuser else 'voter'}
        )
        
        # If profile already existed but role wasn't set for admin users
        if not created and user.is_superuser and not profile.role == 'admin':
            profile.role = 'admin'
            profile.save()
            
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': profile.role,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser
        })


class AdminUserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Admins only
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
            raise PermissionDenied('Only admins can list users.')

        users = User.objects.all().select_related('profile').order_by('username')
        data = [
            {
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'role': getattr(u.profile, 'role', 'voter'),
                'is_superuser': u.is_superuser,
                'is_staff': u.is_staff,
            }
            for u in users
        ]
        return Response(data)


class AdminUpdateUserRoleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        # Admins only
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
            raise PermissionDenied('Only admins can update roles.')

        role = request.data.get('role')
        valid_roles = [choice[0] for choice in UserProfile.USER_ROLES]
        if role not in valid_roles:
            return Response({'detail': 'Invalid role.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            target_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        profile, _ = UserProfile.objects.get_or_create(user=target_user)
        profile.role = role
        profile.save()

        return Response({'detail': 'Role updated successfully.', 'user_id': target_user.id, 'role': profile.role})
