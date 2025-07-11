from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.socialaccount.models import SocialAccount
import requests
from io import BytesIO
from django.core.files.base import ContentFile

@receiver(post_save, sender=SocialAccount)
def update_user_profile_from_social(sender, instance, created, **kwargs):
    """Update user profile with data from social account"""
    if not created:
        return
    
    user = instance.user
    extra_data = instance.extra_data
    
    # Handle Google profile picture
    if instance.provider == 'google' and 'picture' in extra_data:
        try:
            # Download profile picture from Google
            response = requests.get(extra_data['picture'])
            if response.status_code == 200:
                # Save the image to the user's profile
                img_content = ContentFile(response.content)
                user.profile_picture.save(
                    f'google_profile_{user.id}.jpg',
                    img_content,
                    save=True
                )
        except Exception as e:
            print(f"Error downloading Google profile picture: {e}")
