from django.core.management.base import BaseCommand
from core.views import generate_image_free_services_with_tracking
import tempfile
import os

class Command(BaseCommand):
    help = 'Test which image generation services are currently working'

    def handle(self, *args, **options):
        self.stdout.write("=== Testing Current Image Generation Services ===")
        
        test_prompt = "a simple red circle on white background"
        
        try:
            # Test the image generation pipeline
            self.stdout.write(f"🧪 Testing with prompt: '{test_prompt}'")
            
            image_content, source, metadata = generate_image_free_services_with_tracking(test_prompt)
            
            if image_content:
                # Save to temporary file to analyze
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    tmp_file.write(image_content.read())
                    tmp_path = tmp_file.name
                
                # Check file size
                file_size = os.path.getsize(tmp_path) / 1024  # KB
                self.stdout.write(f"✅ Image generated successfully!")
                self.stdout.write(f"📏 File size: {file_size:.1f} KB")
                self.stdout.write(f"🎯 Source: {source}")
                self.stdout.write(f"📋 Service: {metadata.get('service_name', 'Unknown')}")
                
                # Determine what this means
                if source == 'mock':
                    self.stdout.write("   ⚠️  This means all external APIs are currently unavailable")
                else:
                    self.stdout.write("   ✅ External API is working!")
                
                # Clean up
                os.unlink(tmp_path)
                
            else:
                self.stdout.write("❌ No image generated")
                
        except Exception as e:
            self.stdout.write(f"❌ Error during test: {e}")
