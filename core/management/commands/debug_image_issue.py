from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import GeneratedImage
import os

class Command(BaseCommand):
    help = 'Debug the specific image viewing issue'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Debugging image viewing issue...")
        
        # Check settings
        self.stdout.write(f"📁 MEDIA_ROOT: {settings.MEDIA_ROOT}")
        self.stdout.write(f"🌐 MEDIA_URL: {settings.MEDIA_URL}")
        self.stdout.write(f"🐛 DEBUG: {settings.DEBUG}")
        
        # Check if directories exist
        media_exists = os.path.exists(settings.MEDIA_ROOT)
        gen_images_path = os.path.join(settings.MEDIA_ROOT, 'generated_images')
        gen_images_exists = os.path.exists(gen_images_path)
        
        self.stdout.write(f"📂 Media root exists: {media_exists}")
        self.stdout.write(f"📂 Generated images folder exists: {gen_images_exists}")
        
        if gen_images_exists:
            files = os.listdir(gen_images_path)
            self.stdout.write(f"📄 Files in generated_images: {len(files)}")
            for file in files[:3]:
                self.stdout.write(f"   - {file}")
        
        # Check database records
        images = GeneratedImage.objects.all()
        self.stdout.write(f"\n📊 Total images in database: {images.count()}")
        
        if images.exists():
            first_image = images.first()
            self.stdout.write(f"\n🖼️  First image details:")
            self.stdout.write(f"   ID: {first_image.id}")
            self.stdout.write(f"   User: {first_image.user.username}")
            self.stdout.write(f"   Prompt: {first_image.prompt[:50]}...")
            self.stdout.write(f"   Image field: {first_image.image}")
            
            if first_image.image:
                self.stdout.write(f"   Image name: {first_image.image.name}")
                self.stdout.write(f"   Image path: {first_image.image.path}")
                self.stdout.write(f"   Image URL: {first_image.image.url}")
                self.stdout.write(f"   File exists: {os.path.exists(first_image.image.path)}")
                
                if os.path.exists(first_image.image.path):
                    file_size = os.path.getsize(first_image.image.path)
                    self.stdout.write(f"   File size: {file_size} bytes")
                else:
                    self.stdout.write("   ❌ File does not exist on disk!")
            else:
                self.stdout.write("   ❌ No image file associated!")
        
        # Test URL pattern
        if images.exists():
            test_image = images.first()
            self.stdout.write(f"\n🔗 Test URLs:")
            self.stdout.write(f"   Post detail URL: /post/{test_image.id}/")
            self.stdout.write(f"   Expected image URL: {test_image.image.url if test_image.image else 'No image'}")
