from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Test email configuration'

    def handle(self, *args, **options):
        self.stdout.write("📧 Testing email configuration...")
        
        try:
            send_mail(
                'Test Email from AI Social Platform',
                'This is a test email to verify email configuration.',
                settings.DEFAULT_FROM_EMAIL,
                ['test@example.com'],
                fail_silently=False,
            )
            self.stdout.write("✅ Email sent successfully!")
            self.stdout.write(f"   Backend: {settings.EMAIL_BACKEND}")
            
            if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
                self.stdout.write("   📝 Check your console for the email content")
            
        except Exception as e:
            self.stdout.write(f"❌ Email failed: {str(e)}")
            self.stdout.write("   Check your email configuration in settings.py")
