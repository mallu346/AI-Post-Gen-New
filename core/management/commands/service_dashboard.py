from django.core.management.base import BaseCommand
from core.models import GeneratedImage
from django.utils import timezone
from datetime import timedelta
import json

class Command(BaseCommand):
    help = 'Display a comprehensive service dashboard'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("🚀 AI IMAGE GENERATION SERVICE DASHBOARD")
        self.stdout.write("=" * 60)
        
        # Test current service availability
        self.stdout.write("\n📡 CURRENT SERVICE STATUS")
        self.stdout.write("-" * 30)
        
        try:
            from core.views import generate_image_free_services_with_tracking
            image_content, source, metadata = generate_image_free_services_with_tracking("test")
            
            if source == 'mock':
                self.stdout.write("🔴 All external APIs are DOWN - using fallback")
            else:
                service_name = metadata.get('service_name', source)
                self.stdout.write(f"🟢 {service_name} is ONLINE and working")
                
        except Exception as e:
            self.stdout.write(f"🔴 Error testing services: {e}")
        
        # Historical statistics
        self.stdout.write("\n📊 HISTORICAL STATISTICS")
        self.stdout.write("-" * 30)
        
        total_images = GeneratedImage.objects.count()
        self.stdout.write(f"Total images generated: {total_images}")
        
        if total_images > 0:
            # Service breakdown
            service_stats = {}
            for image in GeneratedImage.objects.all():
                source = image.generation_source
                if source not in service_stats:
                    service_stats[source] = {
                        'count': 0,
                        'display_name': image.get_service_display_name()
                    }
                service_stats[source]['count'] += 1
            
            self.stdout.write("\nService Usage:")
            for source, stats in service_stats.items():
                percentage = (stats['count'] / total_images) * 100
                bar = "█" * int(percentage / 5)  # Simple bar chart
                self.stdout.write(f"  {stats['display_name']:<20} {stats['count']:>3} ({percentage:>5.1f}%) {bar}")
        
        # Recent activity (last 24 hours)
        self.stdout.write("\n⏰ RECENT ACTIVITY (Last 24 Hours)")
        self.stdout.write("-" * 30)
        
        yesterday = timezone.now() - timedelta(days=1)
        recent_images = GeneratedImage.objects.filter(created_at__gte=yesterday).order_by('-created_at')
        
        if recent_images:
            self.stdout.write(f"Images generated: {recent_images.count()}")
            
            recent_services = {}
            for image in recent_images:
                source = image.generation_source
                if source not in recent_services:
                    recent_services[source] = 0
                recent_services[source] += 1
            
            self.stdout.write("Services used:")
            for source, count in recent_services.items():
                display_name = GeneratedImage.SERVICE_CHOICES
                name = next((choice[1] for choice in display_name if choice[0] == source), source)
                self.stdout.write(f"  {name}: {count} images")
        else:
            self.stdout.write("No images generated in the last 24 hours")
        
        # Performance metrics
        self.stdout.write("\n⚡ PERFORMANCE METRICS")
        self.stdout.write("-" * 30)
        
        if total_images > 0:
            # Average file sizes by service
            for source_code, source_name in GeneratedImage.SERVICE_CHOICES:
                images = GeneratedImage.objects.filter(generation_source=source_code)
                if images.exists():
                    total_size = sum(img.get_file_size_kb() for img in images)
                    avg_size = total_size / images.count()
                    self.stdout.write(f"{source_name:<20} Avg size: {avg_size:>6.1f} KB")
        
        # Recommendations
        self.stdout.write("\n💡 RECOMMENDATIONS")
        self.stdout.write("-" * 30)
        
        if total_images > 0:
            mock_count = GeneratedImage.objects.filter(generation_source='mock').count()
            mock_percentage = (mock_count / total_images) * 100
            
            if mock_percentage > 50:
                self.stdout.write("⚠️  High fallback usage - consider checking API keys")
            elif mock_percentage > 20:
                self.stdout.write("⚠️  Moderate fallback usage - APIs may be intermittent")
            else:
                self.stdout.write("✅ Good API reliability - low fallback usage")
            
            pollinations_count = GeneratedImage.objects.filter(generation_source='pollinations').count()
            if pollinations_count > total_images * 0.8:
                self.stdout.write("✅ Pollinations AI is your most reliable service")
        
        self.stdout.write("\n" + "=" * 60)
