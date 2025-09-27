from rest_framework import generics, permissions, status, mixins, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from .models import Election, Candidate, Vote, UserProfile, ElectionLog, VoterEligibility
from django.contrib.auth import get_user_model
from .serializers import (
    ElectionSerializer, ElectionDetailSerializer, VoteSerializer,
    MyVoteSerializer, ResultSerializer, AdminElectionSerializer,
    AdminCandidateSerializer
)
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.utils import timezone
from django.utils.timezone import make_aware, is_naive
from django.shortcuts import get_object_or_404

class ElectionListView(generics.ListAPIView):
    queryset = Election.objects.all()
    serializer_class = ElectionSerializer
    permission_classes = [permissions.AllowAny]

class ElectionDetailView(generics.RetrieveAPIView):
    queryset = Election.objects.all()
    serializer_class = ElectionDetailSerializer
    permission_classes = [permissions.AllowAny]

class VoteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = VoteSerializer(data=request.data, context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            # Normalize common serializer error shapes into a single detail string
            detail = None
            if isinstance(e.detail, dict):
                for key in ['non_field_errors', 'election', 'candidate', 'rank', 'detail']:
                    if key in e.detail and e.detail[key]:
                        msg = e.detail[key]
                        detail = msg[0] if isinstance(msg, list) else str(msg)
                        break
                if detail is None:
                    # Fallback to first value in dict
                    first = next(iter(e.detail.values()))
                    detail = first[0] if isinstance(first, list) else str(first)
            else:
                detail = str(e.detail)
            return Response({'detail': detail or 'Invalid vote request.'}, status=status.HTTP_400_BAD_REQUEST)

        vote = serializer.save()

        ElectionLog.objects.create(
            election=vote.election,
            user=request.user,
            action='vote_cast',
            details=f'Voted for {vote.candidate.name}'
        )

        return Response({'detail': 'Vote cast successfully', 'vote_id': vote.id}, status=status.HTTP_201_CREATED)

class MyVotesView(generics.ListAPIView):
    serializer_class = MyVoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Vote.objects.filter(voter=self.request.user)

class ResultsView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request, election_id):
        try:
            election = Election.objects.get(pk=election_id)
        except Election.DoesNotExist:
            return Response({'detail': 'Election not found.'}, status=404)
        # Compare timezone-aware datetimes
        now = timezone.now()
        end = election.end_time
        if is_naive(end):
            end = make_aware(end)
        if now < end:
            return Response({'detail': 'Results are locked until the election ends.'}, status=403)
        serializer = ResultSerializer(election)
        return Response(serializer.data)


class AdminElectionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for admin election management.
    """
    serializer_class = AdminElectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Allow admins and election managers to manage elections
        if not hasattr(self.request.user, 'profile') or self.request.user.profile.role not in ['admin', 'election_manager']:
            raise PermissionDenied("You do not have permission to perform this action.")
        return Election.objects.all().order_by('-created_at')
    
    def perform_create(self, serializer):
        # Set the created_by field to the current user
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def launch(self, request, pk=None):
        """
        Launch/activate an election.
        """
        election = self.get_object()
        
        # Check if user is allowed (admin or election manager)
        if not hasattr(request.user, 'profile') or request.user.profile.role not in ['admin', 'election_manager']:
            raise PermissionDenied("You do not have permission to launch elections.")
        
        # Validate that election has at least one candidate
        if not election.candidates.exists():
            return Response(
                {'detail': 'Cannot launch an election without at least one candidate.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate that end time is in the future
        if election.end_time <= timezone.now():
            return Response(
                {'detail': 'Cannot launch an election with an end time in the past.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Activate the election
        election.is_active = True
        election.save()
        
        return Response(
            {'detail': 'Election launched successfully.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """
        Close/deactivate an election.
        """
        election = self.get_object()
        
        # Check if user is allowed (admin or election manager)
        if not hasattr(request.user, 'profile') or request.user.profile.role not in ['admin', 'election_manager']:
            raise PermissionDenied("You do not have permission to close elections.")
        
        # Deactivate the election
        election.is_active = False
        election.save()
        
        return Response(
            {'detail': 'Election closed successfully.'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def add_voter(self, request, pk=None):
        election = self.get_object()
        if not hasattr(request.user, 'profile') or request.user.profile.role not in ['admin', 'election_manager']:
            raise PermissionDenied("You do not have permission to modify eligibility.")

        user_id = request.data.get('user_id')
        username = request.data.get('username')
        if not user_id and not username:
            return Response({'detail': 'Provide user_id or username.'}, status=status.HTTP_400_BAD_REQUEST)

        UserModel = get_user_model()
        try:
            if user_id:
                voter = UserModel.objects.get(pk=user_id)
            else:
                voter = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        VoterEligibility.objects.get_or_create(election=election, voter=voter)
        ElectionLog.objects.create(
            election=election,
            user=request.user,
            action='voter_added',
            details=f'Added voter {voter.username}'
        )
        return Response({'detail': 'Voter added to eligibility.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def remove_voter(self, request, pk=None):
        election = self.get_object()
        if not hasattr(request.user, 'profile') or request.user.profile.role not in ['admin', 'election_manager']:
            raise PermissionDenied("You do not have permission to modify eligibility.")

        user_id = request.data.get('user_id')
        username = request.data.get('username')
        if not user_id and not username:
            return Response({'detail': 'Provide user_id or username.'}, status=status.HTTP_400_BAD_REQUEST)

        UserModel = get_user_model()
        try:
            if user_id:
                voter = UserModel.objects.get(pk=user_id)
            else:
                voter = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        VoterEligibility.objects.filter(election=election, voter=voter).delete()
        return Response({'detail': 'Voter removed from eligibility.'}, status=status.HTTP_200_OK)
