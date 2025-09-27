from rest_framework import serializers
from .models import Election, Candidate, Vote, UserProfile, VoterEligibility
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timezone import make_aware, is_naive

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['id', 'name']

class AdminCandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['id', 'name', 'description', 'position', 'order', 'is_active']
        read_only_fields = ['id']

class ElectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Election
        fields = ['id', 'name', 'description', 'start_time', 'end_time', 'voting_start_time', 'voting_end_time']

class AdminElectionSerializer(serializers.ModelSerializer):
    candidates = AdminCandidateSerializer(many=True, required=False)
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.filter(profile__role__in=['admin', 'election_manager']),
        required=False
    )
    
    class Meta:
        model = Election
        fields = [
            'id', 'name', 'description', 'election_type', 'visibility',
            'start_time', 'end_time', 'voting_start_time', 'voting_end_time',
            'max_votes_per_voter', 'require_confirmation', 'is_active',
            'candidates', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        if 'start_time' in data and 'end_time' in data and data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("End time must be after start time.")
        if 'voting_start_time' in data and 'voting_end_time' in data:
            if data['voting_start_time'] >= data['voting_end_time']:
                raise serializers.ValidationError("Voting end time must be after voting start time.")
        return data
    
    def create(self, validated_data):
        candidates_data = validated_data.pop('candidates', [])
        election = Election.objects.create(**validated_data)
        
        for candidate_data in candidates_data:
            Candidate.objects.create(election=election, **candidate_data)
            
        return election
    
    def update(self, instance, validated_data):
        candidates_data = validated_data.pop('candidates', None)
        
        # Update election fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update or create candidates if provided
        if candidates_data is not None:
            # Get existing candidate IDs
            existing_candidate_ids = set(instance.candidates.values_list('id', flat=True))
            updated_candidate_ids = set()
            
            # Update or create candidates
            for candidate_data in candidates_data:
                candidate_id = candidate_data.get('id')
                if candidate_id and instance.candidates.filter(id=candidate_id).exists():
                    # Update existing candidate
                    Candidate.objects.filter(id=candidate_id).update(**candidate_data)
                    updated_candidate_ids.add(candidate_id)
                else:
                    # Create new candidate
                    if 'id' in candidate_data:
                        candidate_data.pop('id')
                    Candidate.objects.create(election=instance, **candidate_data)
            
            # Delete candidates that were not included in the update
            instance.candidates.exclude(id__in=updated_candidate_ids).delete()
            
        return instance


class ElectionDetailSerializer(serializers.ModelSerializer):
    candidates = CandidateSerializer(many=True, read_only=True)
    class Meta:
        model = Election
        fields = [
            'id', 'name', 'description', 'start_time', 'end_time',
            'voting_start_time', 'voting_end_time', 'election_type',
            'max_votes_per_voter', 'candidates'
        ]

class VoteSerializer(serializers.ModelSerializer):
    candidate = serializers.PrimaryKeyRelatedField(queryset=Candidate.objects.all())
    election = serializers.PrimaryKeyRelatedField(queryset=Election.objects.all())
    
    class Meta:
        model = Vote
        fields = ['election', 'candidate', 'rank']
        extra_kwargs = {
            'rank': {'required': False, 'default': 1}  # Default rank is 1 for single-choice
        }
    def validate(self, data):
        request = self.context.get('request')
        user = request.user if request and hasattr(request, 'user') else None
        
        if not user or not user.is_authenticated:
            raise serializers.ValidationError('Authentication required to vote.')
            
        election = data.get('election')
        candidate = data.get('candidate')
        
        if not election or not candidate:
            raise serializers.ValidationError('Election and candidate are required.')
            
        # Check if candidate belongs to the election
        if candidate.election_id != election.id:
            raise serializers.ValidationError('Invalid candidate for this election.')
            
        # Enforce eligibility for private elections
        if election.visibility == 'private':
            if not VoterEligibility.objects.filter(election=election, voter=user).exists():
                raise serializers.ValidationError('You are not eligible to vote in this election.')
            
        # Check if election is active and currently ongoing
        # is_active flag plus start/end window (timezone-safe)
        now = timezone.now()
        start = election.start_time
        end = election.end_time
        
        # Ensure both start and end times are timezone-aware
        if is_naive(start):
            start = make_aware(start, timezone.get_current_timezone())
        if is_naive(end):
            end = make_aware(end, timezone.get_current_timezone())
            
        # Convert to UTC for consistent comparison
        start_utc = start.astimezone(timezone.utc) if start.tzinfo else start
        end_utc = end.astimezone(timezone.utc) if end.tzinfo else end
        now_utc = now.astimezone(timezone.utc)
        
        if not election.is_active or not (start_utc <= now_utc <= end_utc):
            raise serializers.ValidationError('Election is not active.')
            
        # Enforce daily voting time window
        now_local = timezone.localtime(now)
        now_time = now_local.time()
        start_t = election.voting_start_time
        end_t = election.voting_end_time
        
        within_window = False
        if start_t <= end_t:
            within_window = (start_t <= now_time <= end_t)
        else:
            # Window crosses midnight (e.g., 22:00 - 02:00)
            within_window = (now_time >= start_t or now_time <= end_t)
            
        if not within_window:
            raise serializers.ValidationError('Voting is closed at this time of day.')
            
        existing_votes_qs = Vote.objects.filter(voter=user, election=election)

        # Voting rules by type
        if election.election_type == 'single_choice':
            if existing_votes_qs.exists():
                raise serializers.ValidationError('You have already voted in this election.')
            data['rank'] = 1
        elif election.election_type == 'multiple_choice':
            existing_count = existing_votes_qs.count()
            if existing_count >= election.max_votes_per_voter:
                raise serializers.ValidationError('You have reached the maximum number of votes for this election.')
            # No duplicate candidate
            if existing_votes_qs.filter(candidate=candidate).exists():
                raise serializers.ValidationError('You have already voted for this candidate.')
            data['rank'] = 1
        elif election.election_type == 'ranked_choice':
            # Require rank and within allowed range
            rank = data.get('rank')
            if rank is None:
                raise serializers.ValidationError('Rank is required for ranked choice elections.')
            if rank < 1 or rank > election.max_votes_per_voter:
                raise serializers.ValidationError('Rank must be between 1 and max votes per voter.')
            # Prevent duplicate rank or candidate
            if existing_votes_qs.filter(rank=rank).exists():
                raise serializers.ValidationError('You have already used this rank in this election.')
            if existing_votes_qs.filter(candidate=candidate).exists():
                raise serializers.ValidationError('You have already ranked this candidate.')
        else:
            raise serializers.ValidationError('Unsupported election type.')
            
        return data
    def create(self, validated_data):
        request = self.context.get('request')
        ip_address = None
        user_agent = ''
        if request is not None:
            ip_address = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT', '')
        return Vote.objects.create(
            voter=request.user,
            ip_address=ip_address,
            user_agent=user_agent,
            **validated_data
        )

class MyVoteSerializer(serializers.ModelSerializer):
    election = ElectionSerializer()
    candidate = CandidateSerializer()
    class Meta:
        model = Vote
        fields = ['election', 'candidate', 'timestamp']

class ResultSerializer(serializers.ModelSerializer):
    candidates = serializers.SerializerMethodField()
    class Meta:
        model = Election
        fields = ['id', 'name', 'candidates']
    def get_candidates(self, obj):
        results = []
        for candidate in obj.candidates.all():
            count = Vote.objects.filter(election=obj, candidate=candidate).count()
            results.append({'id': candidate.id, 'name': candidate.name, 'votes': count})
        return results