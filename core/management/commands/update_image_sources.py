from django.core.management.base import BaseCommand
from core.models import GeneratedImage

class Command(BaseCommand):
    help = 'Update generation_source for existing images based on file analysis'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        self.stdout.write("=== Updating Image Sources ===")
        
        # Get images with unknown source
        unknown_images = GeneratedImage.objects.filter(generation_source='unknown')
        
        if not unknown_images:
            self.stdout.write("✅ All images already have source information")
            return
        
        self.stdout.write(f"📊 Found {unknown_images.count()} images with unknown source")
        
        updated_count = 0
        
        for img in unknown_images:
            if img.image:
                detected_source = img.detect_generation_source()
                
                if options['dry_run']:
                    self.stdout.write(f"Would update {str(img.id)[:8]}... to {detected_source}")
                else:
                    img.generation_source = detected_source
                    img.save(update_fields=['generation_source'])
                    self.stdout.write(f"Updated {str(img.id)[:8]}... to {detected_source}")
                
                updated_count += 1
        
        if options['dry_run']:
            self.stdout.write(f"Dry run complete. Would update {updated_count} images")
        else:
            self.stdout.write(f"✅ Updated {updated_count} images")
