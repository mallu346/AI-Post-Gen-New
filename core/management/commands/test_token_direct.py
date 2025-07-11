from django.core.management.base import BaseCommand
from django.conf import settings
import requests

class Command(BaseCommand):
    help = 'Test Hugging Face token directly'

    def handle(self, *args, **options):
        token = getattr(settings, 'HUGGINGFACE_API_TOKEN', None)
        
        if not token:
            self.stdout.write(self.style.ERROR('❌ No token found'))
            return
        
        self.stdout.write(f'Testing token: {token[:4]}...{token[-4:]}')
        
        # Test 1: Check token validity
        self.stdout.write('\n=== Test 1: Token Validation ===')
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get("https://huggingface.co/api/whoami", headers=headers, timeout=10)
            
            self.stdout.write(f'Status Code: {response.status_code}')
            self.stdout.write(f'Response Headers: {dict(response.headers)}')
            
            if response.status_code == 200:
                data = response.json()
                self.stdout.write(self.style.SUCCESS(f'✅ Token valid! User: {data.get("name", "Unknown")}'))
            elif response.status_code == 401:
                self.stdout.write(self.style.ERROR('❌ Token is invalid or expired'))
                self.stdout.write(f'Response: {response.text}')
            else:
                self.stdout.write(self.style.WARNING(f'⚠️ Unexpected status: {response.status_code}'))
                self.stdout.write(f'Response: {response.text}')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
        
        # Test 2: Check model access
        self.stdout.write('\n=== Test 2: Model Access ===')
        try:
            model_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
            headers = {"Authorization": f"Bearer {token}"}
            
            # Just check if we can reach the model endpoint
            response = requests.get(model_url, headers=headers, timeout=10)
            self.stdout.write(f'Model endpoint status: {response.status_code}')
            
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS('✅ Model endpoint accessible'))
            else:
                self.stdout.write(f'Response: {response.text[:200]}...')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Model access error: {str(e)}'))
