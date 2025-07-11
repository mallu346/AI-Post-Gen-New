from django.core.management.base import BaseCommand
from django.urls import reverse
from django.conf import settings

class Command(BaseCommand):
    help = 'Check if allauth is properly configured'

    def handle(self, *args, **options):
        self.stdout.write("=== Checking Allauth Configuration ===")
        
        # Check if allauth is in INSTALLED_APPS
        if 'allauth' in settings.INSTALLED_APPS:
            self.stdout.write("✅ allauth is in INSTALLED_APPS")
        else:
            self.stdout.write("❌ allauth is NOT in INSTALLED_APPS")
        
        if 'allauth.account' in settings.INSTALLED_APPS:
            self.stdout.write("✅ allauth.account is in INSTALLED_APPS")
        else:
            self.stdout.write("❌ allauth.account is NOT in INSTALLED_APPS")
        
        if 'allauth.socialaccount' in settings.INSTALLED_APPS:
            self.stdout.write("✅ allauth.socialaccount is in INSTALLED_APPS")
        else:
            self.stdout.write("❌ allauth.socialaccount is NOT in INSTALLED_APPS")
        
        # Check authentication backends
        auth_backends = getattr(settings, 'AUTHENTICATION_BACKENDS', [])
        if 'allauth.account.auth_backends.AuthenticationBackend' in auth_backends:
            self.stdout.write("✅ allauth authentication backend is configured")
        else:
            self.stdout.write("❌ allauth authentication backend is NOT configured")
        
        # Try to reverse allauth URLs
        try:
            login_url = reverse('account_login')
            self.stdout.write(f"✅ account_login URL: {login_url}")
        except Exception as e:
            self.stdout.write(f"❌ account_login URL error: {e}")
        
        try:
            signup_url = reverse('account_signup')
            self.stdout.write(f"✅ account_signup URL: {signup_url}")
        except Exception as e:
            self.stdout.write(f"❌ account_signup URL error: {e}")
        
        try:
            logout_url = reverse('account_logout')
            self.stdout.write(f"✅ account_logout URL: {logout_url}")
        except Exception as e:
            self.stdout.write(f"❌ account_logout URL error: {e}")
        
        # Check SITE_ID
        site_id = getattr(settings, 'SITE_ID', None)
        if site_id:
            self.stdout.write(f"✅ SITE_ID is set to: {site_id}")
        else:
            self.stdout.write("❌ SITE_ID is not set")
