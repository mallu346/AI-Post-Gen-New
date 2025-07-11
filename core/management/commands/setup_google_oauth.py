from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.conf import settings

class Command(BaseCommand):
    help = 'Set up Google OAuth for the site'

    def add_arguments(self, parser):
        parser.add_argument('--client-id', type=str, help='Google OAuth Client ID')
        parser.add_argument('--client-secret', type=str, help='Google OAuth Client Secret')

    def handle(self, *args, **options):
        self.stdout.write("=== Setting up Google OAuth ===")
        
        # Get or create the site
        site, created = Site.objects.get_or_create(
            id=settings.SITE_ID,
            defaults={
                'domain': 'localhost:8000',
                'name': 'AI Social Platform'
            }
        )
        
        if created:
            self.stdout.write(f"✅ Created site: {site.domain}")
        else:
            self.stdout.write(f"✅ Site exists: {site.domain}")

        # Get credentials from command line or prompt user
        client_id = options.get('client_id')
        client_secret = options.get('client_secret')
        
        if not client_id:
            self.stdout.write("\n🔑 Google OAuth Setup")
            self.stdout.write("To get your Google OAuth credentials:")
            self.stdout.write("1. Go to https://console.cloud.google.com/")
            self.stdout.write("2. Create a new project or select existing one")
            self.stdout.write("3. Enable Google+ API")
            self.stdout.write("4. Go to 'Credentials' and create 'OAuth 2.0 Client IDs'")
            self.stdout.write("5. Add these redirect URIs:")
            self.stdout.write("   - http://localhost:8000/accounts/google/login/callback/")
            self.stdout.write("   - http://127.0.0.1:8000/accounts/google/login/callback/")
            self.stdout.write("\nOnce you have your credentials, run:")
            self.stdout.write("python manage.py setup_google_oauth --client-id YOUR_ID --client-secret YOUR_SECRET")
            return

        if not client_secret:
            self.stdout.write("❌ Both --client-id and --client-secret are required")
            return

        # Create or update Google social app
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google',
                'client_id': client_id,
                'secret': client_secret,
            }
        )

        if not created:
            google_app.client_id = client_id
            google_app.secret = client_secret
            google_app.save()

        # Add the site to the social app
        google_app.sites.add(site)

        if created:
            self.stdout.write("✅ Created Google social application")
        else:
            self.stdout.write("✅ Updated Google social application")

        self.stdout.write(
            self.style.SUCCESS(
                f"\n🎉 Google authentication is now configured!\n"
                f"Test URLs:\n"
                f"- Login: http://localhost:8000/accounts/login/\n"
                f"- Google OAuth: http://localhost:8000/accounts/google/login/\n"
                f"- Signup: http://localhost:8000/accounts/signup/\n"
            )
        )
