from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.conf import settings

class Command(BaseCommand):
    help = 'Set up Google authentication for the site'

    def add_arguments(self, parser):
        parser.add_argument('--client-id', type=str, help='Google OAuth Client ID')
        parser.add_argument('--client-secret', type=str, help='Google OAuth Client Secret')

    def handle(self, *args, **options):
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

        # Get credentials from command line or environment
        client_id = options.get('client_id') or getattr(settings, 'GOOGLE_CLIENT_ID', '')
        client_secret = options.get('client_secret') or getattr(settings, 'GOOGLE_CLIENT_SECRET', '')

        if not client_id or not client_secret:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  Google credentials not provided. Please either:\n"
                    "1. Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to your .env file\n"
                    "2. Run: python manage.py setup_google_auth --client-id YOUR_ID --client-secret YOUR_SECRET"
                )
            )
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
                f"Visit: http://localhost:8000/accounts/google/login/ to test\n"
                f"Make sure to add http://localhost:8000/accounts/google/login/callback/ "
                f"to your Google OAuth redirect URIs"
            )
        )
