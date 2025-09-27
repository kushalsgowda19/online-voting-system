from django.contrib import admin
from .models import Election, Candidate, Vote, UserProfile, VoterEligibility, ElectionLog

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__email']

@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'election_type', 'visibility', 'start_time', 'end_time', 'is_active', 'created_by']
    list_filter = ['election_type', 'visibility', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    date_hierarchy = 'created_at'

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['name', 'election', 'position', 'order', 'is_active']
    list_filter = ['is_active', 'election', 'created_at']
    search_fields = ['name', 'description', 'position']
    ordering = ['election', 'order', 'name']

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['voter', 'election', 'candidate', 'rank', 'timestamp']
    list_filter = ['election', 'timestamp']
    search_fields = ['voter__username', 'election__name', 'candidate__name']
    date_hierarchy = 'timestamp'

@admin.register(VoterEligibility)
class VoterEligibilityAdmin(admin.ModelAdmin):
    list_display = ['election', 'voter', 'is_invited', 'invitation_sent_at']
    list_filter = ['is_invited', 'election', 'created_at']
    search_fields = ['election__name', 'voter__username']

@admin.register(ElectionLog)
class ElectionLogAdmin(admin.ModelAdmin):
    list_display = ['election', 'user', 'action', 'timestamp']
    list_filter = ['action', 'election', 'timestamp']
    search_fields = ['election__name', 'user__username', 'details']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']
