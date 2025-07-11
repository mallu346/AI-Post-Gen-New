from django.core.management.base import BaseCommand
from django.urls import get_resolver
from django.conf import settings

class Command(BaseCommand):
    help = 'Debug URL configuration'

    def handle(self, *args, **options):
        self.stdout.write("=== URL Configuration Debug ===")
        
        # Get the root URL resolver
        resolver = get_resolver()
        
        def print_urls(urlpatterns, prefix='', depth=0):
            indent = "  " * depth
            for pattern in urlpatterns:
                if hasattr(pattern, 'url_patterns'):
                    # This is an include() pattern
                    self.stdout.write(f"{indent}📁 {prefix}{pattern.pattern} -> INCLUDE")
                    if str(pattern.pattern) == 'accounts/':
                        self.stdout.write(f"{indent}   🔍 Found accounts/ include!")
                        try:
                            print_urls(pattern.url_patterns, prefix + str(pattern.pattern), depth + 1)
                        except Exception as e:
                            self.stdout.write(f"{indent}   ❌ Error loading included URLs: {e}")
                    elif depth < 2:  # Limit depth to avoid too much output
                        print_urls(pattern.url_patterns, prefix + str(pattern.pattern), depth + 1)
                else:
                    # This is a regular URL pattern
                    name = getattr(pattern, 'name', 'NO_NAME')
                    self.stdout.write(f"{indent}📄 {prefix}{pattern.pattern} -> {name}")
        
        self.stdout.write("Root URL patterns:")
        print_urls(resolver.url_patterns)
        
        # Check if allauth URLs are accessible
        self.stdout.write("\n=== Testing allauth import ===")
        try:
            import allauth.urls
            self.stdout.write("✅ allauth.urls can be imported")
            self.stdout.write(f"   allauth.urls has {len(allauth.urls.urlpatterns)} patterns")
            
            # Show first few allauth patterns
            for i, pattern in enumerate(allauth.urls.urlpatterns[:5]):
                name = getattr(pattern, 'name', 'NO_NAME')
                self.stdout.write(f"   Pattern {i}: {pattern.pattern} -> {name}")
                
        except Exception as e:
            self.stdout.write(f"❌ Error importing allauth.urls: {e}")
