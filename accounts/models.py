from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from elections.models import UserProfile as ElectionsUserProfile

# Import UserProfile from elections app
UserProfile = ElectionsUserProfile

# Signal to create a profile when a new user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # For existing superusers, set role to admin
        role = 'admin' if instance.is_superuser else 'voter'
        UserProfile.objects.create(user=instance, role=role)

# Signal to save the profile when the user is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
