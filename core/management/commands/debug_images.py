from django.core.management.base import BaseCommand
from core.models import GeneratedImage

class Command(BaseCommand):
    help = 'Debug images in database'

    def handle(self, *args, **options):
        self.stdout.write("=== Image Database Debug ===")
        
        # Get all images
        all_images = GeneratedImage.objects.all()
        self.stdout.write(f"Total images in database: {all_images.count()}")
        
        if all_images.count() == 0:
            self.stdout.write("❌ No images found in database!")
            self.stdout.write("Try generating some images first.")
            return
        
        self.stdout.write("\n=== Recent Images ===")
        recent_images = all_images.order_by('-created_at')[:10]
        
        for img in recent_images:
            self.stdout.write(f"\n📸 Image ID: {img.id}")
            self.stdout.write(f"   User: {img.user.username}")
            self.stdout.write(f"   Prompt: {img.prompt[:50]}...")
            self.stdout.write(f"   Public: {img.is_public}")
            self.stdout.write(f"   Created: {img.created_at}")
            self.stdout.write(f"   URL: /post/{img.id}/")
            
            # Check if image file exists
            if img.image:
                self.stdout.write(f"   File: ✅ {img.image.name}")
            else:
                self.stdout.write(f"   File: ❌ Missing")
        
        # Check the specific ID from the error
        problem_id = "9d3f6ff6-a38a-48ba-a0c7-566b5fbcc5c4"
        self.stdout.write(f"\n=== Checking Problem ID: {problem_id} ===")
        
        try:
            problem_image = GeneratedImage.objects.get(id=problem_id)
            self.stdout.write(f"✅ Image found!")
            self.stdout.write(f"   User: {problem_image.user.username}")
            self.stdout.write(f"   Public: {problem_image.is_public}")
            self.stdout.write(f"   Prompt: {problem_image.prompt}")
        except GeneratedImage.DoesNotExist:
            self.stdout.write(f"❌ Image with ID {problem_id} does not exist!")
            
            # Suggest valid IDs
            if all_images.exists():
                self.stdout.write("\n✅ Try these valid URLs instead:")
                for img in recent_images[:3]:
                    self.stdout.write(f"   http://127.0.0.1:8000/post/{img.id}/")
