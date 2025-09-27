from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ElectionListView, ElectionDetailView, VoteView, 
    MyVotesView, ResultsView, AdminElectionViewSet
)

# Create a router for admin views
admin_router = DefaultRouter()
admin_router.register(r'admin/elections', AdminElectionViewSet, basename='admin-election')

urlpatterns = [
    # Public endpoints
    path('elections/', ElectionListView.as_view(), name='election-list'),
    path('elections/<int:pk>/', ElectionDetailView.as_view(), name='election-detail'),
    path('vote/', VoteView.as_view(), name='vote'),
    path('my-votes/', MyVotesView.as_view(), name='my-votes'),
    path('results/<int:election_id>/', ResultsView.as_view(), name='results'),
    
    # Admin endpoints
    path('', include(admin_router.urls)),
]