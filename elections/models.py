from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import datetime

class UserProfile(models.Model):
    USER_ROLES = [
        ('admin', 'Admin'),
        ('election_manager', 'Election Manager'),
        ('voter', 'Voter'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=USER_ROLES, default='voter')
    phone = models.CharField(max_length=20, blank=True, default='')
    date_of_birth = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Election(models.Model):
    ELECTION_TYPES = [
        ('single_choice', 'Single Choice'),
        ('multiple_choice', 'Multiple Choice'),
        ('ranked_choice', 'Ranked Choice'),
    ]
    
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    election_type = models.CharField(max_length=20, choices=ELECTION_TYPES, default='single_choice')
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    voting_start_time = models.TimeField(default=datetime.time(0, 0, 0))
    voting_end_time = models.TimeField(default=datetime.time(23, 59, 59))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_elections', null=True, blank=True)
    eligible_voters = models.ManyToManyField(User, through='VoterEligibility', blank=True)
    max_votes_per_voter = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    require_confirmation = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    @property
    def is_ongoing(self):
        from django.utils import timezone
        from django.utils.timezone import is_naive, make_aware, get_current_timezone
        now = timezone.now()
        start = self.start_time
        end = self.end_time
        # Normalize to aware datetimes in the current timezone
        if is_naive(start):
            start = make_aware(start, timezone=get_current_timezone())
        if is_naive(end):
            end = make_aware(end, timezone=get_current_timezone())
        return start <= now <= end

class VoterEligibility(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    is_invited = models.BooleanField(default=False)
    invitation_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('election', 'voter')

class Candidate(models.Model):
    name = models.CharField(max_length=255)
    election = models.ForeignKey(Election, related_name='candidates', on_delete=models.CASCADE)
    description = models.TextField(blank=True, default='')
    position = models.CharField(max_length=100, blank=True, default='')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.election.name})"
    
    class Meta:
        ordering = ['order', 'name']

class Vote(models.Model):
    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    rank = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    encrypted_vote = models.TextField(blank=True, default='')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default='')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('voter', 'election', 'candidate', 'rank')

    def __str__(self):
        return f"{self.voter} voted for {self.candidate} in {self.election}"

class ElectionLog(models.Model):
    LOG_TYPES = [
        ('election_created', 'Election Created'),
        ('election_updated', 'Election Updated'),
        ('vote_cast', 'Vote Cast'),
        ('voter_added', 'Voter Added'),
        ('candidate_added', 'Candidate Added'),
        ('election_started', 'Election Started'),
        ('election_ended', 'Election Ended'),
    ]
    
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=20, choices=LOG_TYPES)
    details = models.TextField(blank=True, default='')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.action} - {self.election.name} - {self.timestamp}"
