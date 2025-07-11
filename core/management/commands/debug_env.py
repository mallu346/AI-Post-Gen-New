from django.core.management.base import BaseCommand
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Debug environment variables'

    def handle(self, *args, **options):
        self.stdout.write('=== Environment Debug ===')
        
        # Check if .env file exists
        env_path = '.env'
        if os.path.exists(env_path):
            self.stdout.write(self.style.SUCCESS(f'✅ .env file found at: {os.path.abspath(env_path)}'))
        else:
            self.stdout.write(self.style.ERROR(f'❌ .env file NOT found at: {os.path.abspath(env_path)}'))
        
        # Check what Django sees
        token = getattr(settings, 'HUGGINGFACE_API_TOKEN', None)
        if token:
            # Show first and last 4 characters for security
            masked_token = f"{token[:4]}...{token[-4:]}" if len(token) > 8 else "***"
            self.stdout.write(f'Token found: {masked_token}')
            self.stdout.write(f'Token length: {len(token)}')
            self.stdout.write(f'Starts with hf_: {token.startswith("hf_")}')
        else:
            self.stdout.write(self.style.ERROR('❌ No token found in Django settings'))
        
        # Check environment variables directly
        env_token = os.environ.get('HUGGINGFACE_API_TOKEN')
        if env_token:
            masked_env = f"{env_token[:4]}...{env_token[-4:]}" if len(env_token) > 8 else "***"
            self.stdout.write(f'Environment token: {masked_env}')
        else:
            self.stdout.write('❌ No token in environment variables')
