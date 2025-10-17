from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile instance when a new User is created."""
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile instance when the User is saved.
    
    Uses get_or_create to handle cases where UserProfile doesn't exist yet,
    such as during OAuth login or when the signal fires before profile creation.
    This prevents RelatedObjectDoesNotExist errors during Google OAuth login.
    """
    user_profile, created = UserProfile.objects.get_or_create(user=instance)
    # Only save if it already existed (not newly created)
    if not created:
        user_profile.save()
