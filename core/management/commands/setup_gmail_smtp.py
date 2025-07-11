from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Instructions for setting up Gmail SMTP'

    def handle(self, *args, **options):
        self.stdout.write("📧 Setting up Gmail SMTP for real email sending...")
        
        self.stdout.write("\n🔐 Steps to set up Gmail App Password:")
        self.stdout.write("1. Go to your Google Account: https://myaccount.google.com/")
        self.stdout.write("2. Navigate to Security > 2-Step Verification")
        self.stdout.write("3. Enable 2-Step Verification if not already enabled")
        self.stdout.write("4. Go to Security > App passwords")
        self.stdout.write("5. Select 'Mail' and generate an app password")
        self.stdout.write("6. Copy the 16-character app password")
        
        self.stdout.write("\n🔧 Update your .env file with:")
        self.stdout.write("   EMAIL_HOST_USER=your-email@gmail.com")
        self.stdout.write("   EMAIL_HOST_PASSWORD=your-16-character-app-password")
        self.stdout.write("   DEFAULT_FROM_EMAIL=AI Social Platform <your-email@gmail.com>")
        
        self.stdout.write("\n⚠️  Important:")
        self.stdout.write("   - Use the APP PASSWORD, not your regular Gmail password")
        self.stdout.write("   - 2-Step Verification must be enabled")
        self.stdout.write("   - Keep your app password secure")
        
        self.stdout.write("\n🧪 Test with:")
        self.stdout.write("   python manage.py test_email_smtp")
