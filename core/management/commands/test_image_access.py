from django.core.management.base import BaseCommand
from django.test import Client
from core.models import GeneratedImage
import requests

class Command(BaseCommand):
    help = 'Test direct image access'

    def handle(self, *args, **options):
        self.stdout.write("🧪 Testing image access...")
        
        images = GeneratedImage.objects.all()
        if not images.exists():
            self.stdout.write("❌ No images in database to test")
            return
        
        test_image = images.first()
        self.stdout.write(f"🖼️  Testing image: {test_image.id}")
        
        # Test 1: Direct file access
        if test_image.image:
            self.stdout.write(f"📁 Image file path: {test_image.image.path}")
            self.stdout.write(f"🌐 Image URL: {test_image.image.url}")
            
            # Test 2: HTTP access to image
            client = Client()
            try:
                response = client.get(test_image.image.url)
                self.stdout.write(f"📡 Image HTTP response: {response.status_code}")
                if response.status_code == 200:
                    self.stdout.write("✅ Image accessible via HTTP")
                else:
                    self.stdout.write(f"❌ Image not accessible: {response.status_code}")
            except Exception as e:
                self.stdout.write(f"❌ Error accessing image: {e}")
            
            # Test 3: Post detail page
            try:
                response = client.get(f'/post/{test_image.id}/')
                self.stdout.write(f"📄 Post detail response: {response.status_code}")
                if response.status_code == 200:
                    self.stdout.write("✅ Post detail page accessible")
                    # Check if image URL is in the response
                    if test_image.image.url in response.content.decode():
                        self.stdout.write("✅ Image URL found in page content")
                    else:
                        self.stdout.write("❌ Image URL not found in page content")
                else:
                    self.stdout.write(f"❌ Post detail page error: {response.status_code}")
            except Exception as e:
                self.stdout.write(f"❌ Error accessing post detail: {e}")
