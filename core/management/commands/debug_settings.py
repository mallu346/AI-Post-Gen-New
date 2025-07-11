from django.core.management.base import BaseCommand
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Debug Django settings and environment'

    def handle(self, *args, **options):
        self.stdout.write("=== Django Settings Debug ===")
        
        # Check if decouple is working
        try:
            from decouple import config
            self.stdout.write("✅ decouple imported successfully")
            
            # Test reading from .env directly
            replicate_token = config('REPLICATE_API_TOKEN', default='NOT_FOUND')
            hf_token = config('HUGGINGFACE_API_TOKEN', default='NOT_FOUND')
            
            self.stdout.write(f"Direct decouple read - REPLICATE: {replicate_token[:10]}..." if replicate_token != 'NOT_FOUND' else "❌ REPLICATE not found via decouple")
            self.stdout.write(f"Direct decouple read - HUGGINGFACE: {hf_token[:10]}..." if hf_token != 'NOT_FOUND' else "❌ HUGGINGFACE not found via decouple")
            
        except ImportError:
            self.stdout.write("❌ decouple not installed")
        except Exception as e:
            self.stdout.write(f"❌ decouple error: {e}")
        
        # Check Django settings
        self.stdout.write("\n=== Django Settings Values ===")
        replicate_setting = getattr(settings, 'REPLICATE_API_TOKEN', 'NOT_SET')
        hf_setting = getattr(settings, 'HUGGINGFACE_API_TOKEN', 'NOT_SET')
        
        self.stdout.write(f"settings.REPLICATE_API_TOKEN: {replicate_setting}")
        self.stdout.write(f"settings.HUGGINGFACE_API_TOKEN: {hf_setting}")
        
        # Check environment variables
        self.stdout.write("\n=== Environment Variables ===")
        env_replicate = os.environ.get('REPLICATE_API_TOKEN', 'NOT_SET')
        env_hf = os.environ.get('HUGGINGFACE_API_TOKEN', 'NOT_SET')
        
        self.stdout.write(f"os.environ REPLICATE: {env_replicate}")
        self.stdout.write(f"os.environ HUGGINGFACE: {env_hf}")
