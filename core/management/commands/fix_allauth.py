from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Fix allauth configuration and setup Google auth'

    def add_arguments(self, parser):
        parser.add_argument('--client-id', type=str, help='Google OAuth Client ID')
        parser.add_argument('--client-secret', type=str, help='Google OAuth Client Secret')

    def handle(self, *args, **options):
        self.stdout.write("=== Fixing Allauth Configuration ===")
        
        # 1. Check if django.contrib.sites is in INSTALLED_APPS
        try:
            from django.contrib.sites.models import Site
            self.stdout.write("✅ django.contrib.sites is available")
        except ImportError:
            self.stdout.write("❌ django.contrib.sites is NOT available. Please add it to INSTALLED_APPS")
            return
        
        # 2. Check if Site model table exists
        try:
            site_count = Site.objects.count()
            self.stdout.write(f"✅ Site model is working, found {site_count} sites")
        except Exception as e:
            self.stdout.write(f"❌ Error accessing Site model: {e}")
            self.stdout.write("   Run 'python manage.py migrate' to create the table")
            return
        
        # 3. Create or update the default site
        site, created = Site.objects.get_or_create(
            id=settings.SITE_ID,
            defaults={
                'domain': 'localhost:8000',
                'name': 'AI Social Platform'
            }
        )
        
        if created:
            self.stdout.write(f"✅ Created site: {site.domain}")
        else:
            site.domain = 'localhost:8000'
            site.name = 'AI Social Platform'
            site.save()
            self.stdout.write(f"✅ Updated site: {site.domain}")
        
        # 4. Set up Google OAuth if credentials provided
        client_id = options.get('client_id')
        client_secret = options.get('client_secret')
        
        if client_id and client_secret:
            # Create or update Google social app
            google_app, created = SocialApp.objects.get_or_create(
                provider='google',
                defaults={
                    'name': 'Google',
                    'client_id': client_id,
                    'secret': client_secret,
                }
            )
            
            if not created:
                google_app.client_id = client_id
                google_app.secret = client_secret
                google_app.save()
            
            # Add the site to the social app
            google_app.sites.add(site)
            
            if created:
                self.stdout.write("✅ Created Google social application")
            else:
                self.stdout.write("✅ Updated Google social application")
        else:
            self.stdout.write("ℹ️ No Google credentials provided. Skipping Google setup.")
        
        # 5. Create allauth templates directory if it doesn't exist
        templates_dir = os.path.join(settings.BASE_DIR, 'templates', 'account')
        os.makedirs(templates_dir, exist_ok=True)
        self.stdout.write(f"✅ Created templates directory: {templates_dir}")
        
        # 6. Create a basic login template
        login_template_path = os.path.join(templates_dir, 'login.html')
        if not os.path.exists(login_template_path):
            with open(login_template_path, 'w') as f:
                f.write('''{% extends "base.html" %}
{% load i18n %}

{% block title %}{% trans "Sign In" %}{% endblock %}

{% block content %}
<div class="container mt-5">
  <div class="row justify-content-center">
    <div class="col-md-6">
      <div class="card shadow">
        <div class="card-body p-4">
          <h2 class="text-center mb-4">{% trans "Sign In" %}</h2>
          
          <form class="login" method="POST" action="{% url 'account_login' %}">
            {% csrf_token %}
            {{ form.as_p }}
            {% if redirect_field_value %}
            <input type="hidden" name="{{ redirect_field_name }}" value="{{ redirect_field_value }}" />
            {% endif %}
            <div class="d-grid gap-2">
              <button class="btn btn-primary" type="submit">{% trans "Sign In" %}</button>
            </div>
          </form>
          
          <div class="mt-3 text-center">
            <p>
              <a href="{% url 'account_signup' %}">{% trans "Sign up" %}</a> |
              <a href="{% url 'account_reset_password' %}">{% trans "Forgot Password?" %}</a>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
{% endblock %}
''')
            self.stdout.write(f"✅ Created basic login template: {login_template_path}")
        
        # 7. Final instructions
        self.stdout.write("\n=== Next Steps ===")
        self.stdout.write("1. Restart your Django server")
        self.stdout.write("2. Visit http://localhost:8000/accounts/login/")
        self.stdout.write("3. If you want to set up Google auth, run:")
        self.stdout.write("   python manage.py fix_allauth --client-id YOUR_ID --client-secret YOUR_SECRET")
