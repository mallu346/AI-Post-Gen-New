from django.core.management.base import BaseCommand
from django.conf import settings
import os
from pathlib import Path

class Command(BaseCommand):
    help = 'Debug environment variables in detail'

    def handle(self, *args, **options):
        self.stdout.write("=== Detailed Environment Debug ===")
        
        # Check current working directory
        self.stdout.write(f"Current directory: {os.getcwd()}")
        
        # Check if .env file exists
        env_path = Path('.env')
        self.stdout.write(f".env file exists: {env_path.exists()}")
        
        if env_path.exists():
            self.stdout.write(f".env file path: {env_path.absolute()}")
            
            # Read .env file content
            try:
                with open('.env', 'r') as f:
                    content = f.read()
                    self.stdout.write(f".env file size: {len(content)} characters")
                    
                    # Check for tokens in file
                    if 'REPLICATE_API_TOKEN' in content:
                        self.stdout.write("✅ REPLICATE_API_TOKEN found in .env file")
                    else:
                        self.stdout.write("❌ REPLICATE_API_TOKEN not found in .env file")
                        
                    if 'HUGGINGFACE_API_TOKEN' in content:
                        self.stdout.write("✅ HUGGINGFACE_API_TOKEN found in .env file")
                    else:
                        self.stdout.write("❌ HUGGINGFACE_API_TOKEN not found in .env file")
                        
            except Exception as e:
                self.stdout.write(f"Error reading .env: {e}")
        
        # Check environment variables
        self.stdout.write("\n=== Environment Variables ===")
        replicate_token = os.environ.get('REPLICATE_API_TOKEN')
        hf_token = os.environ.get('HUGGINGFACE_API_TOKEN')
        
        if replicate_token:
            self.stdout.write(f"✅ REPLICATE_API_TOKEN in env: {replicate_token[:10]}...")
        else:
            self.stdout.write("❌ REPLICATE_API_TOKEN not in environment")
            
        if hf_token:
            self.stdout.write(f"✅ HUGGINGFACE_API_TOKEN in env: {hf_token[:10]}...")
        else:
            self.stdout.write("❌ HUGGINGFACE_API_TOKEN not in environment")
        
        # Check Django settings
        self.stdout.write("\n=== Django Settings ===")
        try:
            from decouple import config
            replicate_from_config = config('REPLICATE_API_TOKEN', default=None)
            hf_from_config = config('HUGGINGFACE_API_TOKEN', default=None)
            
            if replicate_from_config:
                self.stdout.write(f"✅ REPLICATE_API_TOKEN via decouple: {replicate_from_config[:10]}...")
            else:
                self.stdout.write("❌ REPLICATE_API_TOKEN not found via decouple")
                
            if hf_from_config:
                self.stdout.write(f"✅ HUGGINGFACE_API_TOKEN via decouple: {hf_from_config[:10]}...")
            else:
                self.stdout.write("❌ HUGGINGFACE_API_TOKEN not found via decouple")
                
        except ImportError:
            self.stdout.write("❌ python-decouple not installed")
        except Exception as e:
            self.stdout.write(f"❌ Error with decouple: {e}")
