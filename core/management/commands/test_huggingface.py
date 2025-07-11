from django.core.management.base import BaseCommand
from django.conf import settings
import requests

class Command(BaseCommand):
    help = 'Test Hugging Face API connection'

    def handle(self, *args, **options):
        self.stdout.write("Testing AI API connections...")
        
        # Force reload settings
        from django.conf import settings
        from importlib import reload
        import ai_social_platform.settings as settings_module
        reload(settings_module)
        
        # Get tokens directly from settings module
        replicate_token = getattr(settings_module, 'REPLICATE_API_TOKEN', None)
        hf_token = getattr(settings_module, 'HUGGINGFACE_API_TOKEN', None)
        
        self.stdout.write(f"Direct settings check - REPLICATE: {replicate_token[:10] if replicate_token else 'None'}...")
        self.stdout.write(f"Direct settings check - HUGGINGFACE: {hf_token[:10] if hf_token else 'None'}...")
        
        # Test Replicate
        if replicate_token and replicate_token.strip() and replicate_token != 'NOT_FOUND':
            try:
                import replicate
                client = replicate.Client(api_token=replicate_token)
                self.stdout.write("✅ Replicate API token found and configured")
                
                # Test a simple API call
                try:
                    # This is a lightweight test
                    models = list(client.models.list())
                    self.stdout.write("✅ Replicate API connection successful")
                except Exception as e:
                    self.stdout.write(f"⚠️ Replicate token valid but API test failed: {e}")
                    
            except ImportError:
                self.stdout.write("⚠️ Replicate package not installed. Run: pip install replicate")
            except Exception as e:
                self.stdout.write(f"❌ Replicate error: {e}")
        else:
            self.stdout.write("❌ ⚠️ No Replicate API token found")
        
        # Test Hugging Face
        if hf_token and hf_token.strip():
            try:
                response = requests.get(
                    "https://huggingface.co/api/whoami",
                    headers={"Authorization": f"Bearer {hf_token}"},
                    timeout=10
                )
                if response.status_code == 200:
                    user_info = response.json()
                    self.stdout.write(f"✅ Hugging Face: Connected as {user_info.get('name', 'Unknown')}")
                else:
                    self.stdout.write(f"❌ Hugging Face: Invalid token ({response.status_code})")
            except Exception as e:
                self.stdout.write(f"❌ Hugging Face error: {e}")
        else:
            self.stdout.write("❌ Hugging Face: No token found")
