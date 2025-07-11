from django.core.management.base import BaseCommand
from core.models import GeneratedImage
import os

class Command(BaseCommand):
    help = 'Check which services are generating images'

    def handle(self, *args, **options):
        self.stdout.write("=== Image Generation Sources Analysis ===")
        
        # Get recent images
        recent_images = GeneratedImage.objects.all().order_by('-created_at')[:10]
        
        if not recent_images:
            self.stdout.write("❌ No images found in database")
            return
        
        self.stdout.write(f"📊 Analyzing {recent_images.count()} recent images:")
        
        # Service statistics
        service_stats = {}
        
        for img in recent_images:
            self.stdout.write(f"\n📸 Image ID: {str(img.id)[:8]}...")
            self.stdout.write(f"   Prompt: {img.prompt[:50]}...")
            self.stdout.write(f"   Created: {img.created_at}")
            self.stdout.write(f"   Current source: {img.generation_source}")
            
            if img.image:
                # Check file size
                file_size = img.get_file_size_kb()
                self.stdout.write(f"   File size: {file_size} KB")
                
                # Auto-detect source if unknown
                if img.generation_source == 'unknown':
                    detected_source = img.detect_generation_source()
                    self.stdout.write(f"   🔍 Detected source: {detected_source}")
                
                # Show metadata if available
                if img.generation_metadata:
                    service_name = img.generation_metadata.get('service_name', 'Unknown')
                    self.stdout.write(f"   📋 Service name: {service_name}")
                
                # Update statistics
                source = img.generation_source
                if source not in service_stats:
                    service_stats[source] = 0
                service_stats[source] += 1
            else:
                self.stdout.write("   ❌ No image file associated")
        
        # Display statistics
        self.stdout.write("\n=== Service Statistics ===")
        for service, count in service_stats.items():
            percentage = (count / len(recent_images)) * 100
            self.stdout.write(f"{service}: {count} images ({percentage:.1f}%)")
