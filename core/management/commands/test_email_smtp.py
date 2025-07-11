from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Test SMTP email configuration'

    def add_arguments(self, parser):
        parser.add_argument('--to', type=str, help='Email address to send test email to')

    def handle(self, *args, **options):
        self.stdout.write("📧 Testing SMTP email configuration...")
        
        # Get recipient email
        to_email = options.get('to') or input("Enter email address to send test to: ")
        
        if not to_email:
            self.stdout.write("❌ No email address provided")
            return
        
        try:
            # Test email sending
            send_mail(
                subject='🧪 Test Email from AI Social Platform',
                message='This is a test email to verify SMTP configuration is working correctly!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                fail_silently=False,
            )
            
            self.stdout.write(f"✅ Test email sent successfully to {to_email}!")
            self.stdout.write(f"   From: {settings.DEFAULT_FROM_EMAIL}")
            self.stdout.write(f"   Backend: {settings.EMAIL_BACKEND}")
            self.stdout.write(f"   Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
            
        except Exception as e:
            self.stdout.write(f"❌ Email sending failed: {str(e)}")
            self.stdout.write("\n🔧 Check your configuration:")
            self.stdout.write(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
            self.stdout.write(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
            self.stdout.write(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
            self.stdout.write("   Make sure you're using Gmail App Password, not regular password")
