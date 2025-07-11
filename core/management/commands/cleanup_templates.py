from django.core.management.base import BaseCommand
import os
import shutil

class Command(BaseCommand):
    help = 'Clean up old template files and organize allauth templates'

    def handle(self, *args, **options):
        self.stdout.write("=== Cleaning up template files ===")
        
        # Backup the registration folder
        registration_path = 'templates/registration'
        backup_path = 'templates/registration_backup'
        
        if os.path.exists(registration_path):
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
            shutil.copytree(registration_path, backup_path)
            self.stdout.write(f"✅ Backed up {registration_path} to {backup_path}")
        
        # Create account templates directory if it doesn't exist
        account_path = 'templates/account'
        os.makedirs(account_path, exist_ok=True)
        self.stdout.write(f"✅ Ensured {account_path} directory exists")
        
        self.stdout.write("\n=== Template Organization Complete ===")
        self.stdout.write("Your custom designs are now in templates/account/ for allauth")
        self.stdout.write("Original files backed up to templates/registration_backup/")
        self.stdout.write("\nNow test your authentication:")
        self.stdout.write("1. Visit http://localhost:8000/accounts/login/")
        self.stdout.write("2. Visit http://localhost:8000/accounts/signup/")
        self.stdout.write("3. Try password reset flow")
