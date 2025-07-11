from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
import requests
from io import BytesIO
from django.core.files.base import ContentFile

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        """
        This is called when saving user via allauth registration.
        We override this to set additional data on user object.
        """
        user = super().save_user(request, user, form, commit=False)
        
        # If we have social account data, use it
        social_data = getattr(user, 'socialaccount_set', None)
        if social_data and social_data.exists():
            social_account = social_data.first()
            extra_data = social_account.extra_data
            
            # Get profile data from Google
            if social_account.provider == 'google':
                if not user.first_name and 'given_name' in extra_data:
                    user.first_name = extra_data['given_name']
                if not user.last_name and 'family_name' in extra_data:
                    user.last_name = extra_data['family_name']
                if 'picture' in extra_data:
                    # We'll handle profile picture in a signal
                    pass
        
        if commit:
            user.save()
        return user

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        """
        Saves a newly signed up social login. In case of auto-signup,
        the signup form is not available.
        """
        user = sociallogin.user
        user.set_unusable_password()
        
        # Get extra data from social account
        if sociallogin.account.provider == 'google':
            extra_data = sociallogin.account.extra_data
            
            # Set names if not already set
            if not user.first_name and 'given_name' in extra_data:
                user.first_name = extra_data['given_name']
            if not user.last_name and 'family_name' in extra_data:
                user.last_name = extra_data['family_name']
            
            # Handle profile picture
            if 'picture' in extra_data:
                try:
                    response = requests.get(extra_data['picture'])
                    if response.status_code == 200:
                        img_content = ContentFile(response.content)
                        user.profile_picture.save(
                            f'google_profile_{user.username}.jpg',
                            img_content,
                            save=False
                        )
                except Exception as e:
                    print(f"Error downloading Google profile picture: {e}")
        
        user.save()
        return user
