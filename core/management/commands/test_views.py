from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Test if view functions exist'

    def handle(self, *args, **options):
        self.stdout.write("=== Testing View Functions ===")
        
        try:
            from core import views
            
            # Test if functions exist
            functions_to_test = [
                'download_image',
                'delete_image', 
                'share_image',
                'toggle_image_privacy',
                'bulk_delete_images',
                'gallery',
                'home'
            ]
            
            for func_name in functions_to_test:
                if hasattr(views, func_name):
                    func = getattr(views, func_name)
                    self.stdout.write(f"✅ {func_name}: {func}")
                else:
                    self.stdout.write(f"❌ {func_name}: NOT FOUND")
            
            self.stdout.write("\n=== Import Test ===")
            
            # Test imports
            try:
                from django.http import JsonResponse, HttpResponse, Http404
                self.stdout.write("✅ HTTP imports work")
            except ImportError as e:
                self.stdout.write(f"❌ HTTP imports failed: {e}")
            
            try:
                from django.views.decorators.http import require_POST
                self.stdout.write("✅ require_POST import works")
            except ImportError as e:
                self.stdout.write(f"❌ require_POST import failed: {e}")
                
        except Exception as e:
            self.stdout.write(f"❌ Error importing views: {e}")
