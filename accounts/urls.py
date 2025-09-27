from django.urls import path
from .views import RegisterView, MyTokenObtainPairView, UserDetailsView, AdminUserListView, AdminUpdateUserRoleView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/', UserDetailsView.as_view(), name='user_details'),
    path('admin/users/', AdminUserListView.as_view(), name='admin_users_list'),
    path('admin/users/<int:user_id>/role/', AdminUpdateUserRoleView.as_view(), name='admin_update_user_role'),
]