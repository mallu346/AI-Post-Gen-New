from django.core.management.base import BaseCommand
from django.conf import settings
import requests
import json

class Command(BaseCommand):
    help = 'Detailed Hugging Face token test'

    def handle(self, *args, **options):
        token = getattr(settings, 'HUGGINGFACE_API_TOKEN', None)
        
        if not token:
            self.stdout.write(self.style.ERROR('❌ No token found'))
            return
        
        self.stdout.write(f'Testing token: {token[:4]}...{token[-4:]}')
        self.stdout.write(f'Token length: {len(token)}')
        
        # Test different header formats
        test_cases = [
            {"Authorization": f"Bearer {token}"},
            {"Authorization": f"Bearer {token.strip()}"},
            {"authorization": f"Bearer {token}"},
            {"Authorization": f"Token {token}"},
        ]
        
        for i, headers in enumerate(test_cases, 1):
            self.stdout.write(f'\n=== Test Case {i}: {list(headers.keys())[0]} ===')
            try:
                response = requests.get(
                    "https://huggingface.co/api/whoami", 
                    headers=headers, 
                    timeout=15
                )
                
                self.stdout.write(f'Status: {response.status_code}')
                
                if response.status_code == 200:
                    data = response.json()
                    self.stdout.write(self.style.SUCCESS(f'✅ SUCCESS! User: {data.get("name", "Unknown")}'))
                    self.stdout.write(f'Full response: {json.dumps(data, indent=2)}')
                    break
                else:
                    self.stdout.write(f'Response: {response.text}')
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
        
        # Test if we can reach HuggingFace at all
        self.stdout.write('\n=== Basic Connectivity Test ===')
        try:
            response = requests.get("https://huggingface.co", timeout=10)
            self.stdout.write(f'HuggingFace.co status: {response.status_code}')
        except Exception as e:
            self.stdout.write(f'Cannot reach HuggingFace: {e}')
