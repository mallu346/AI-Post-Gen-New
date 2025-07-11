from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import allauth views directly
from allauth.account.views import LoginView, SignupView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Include allauth URLs
    path('accounts/', include('allauth.urls')),
    
    # Also add direct allauth view mappings for critical paths
    path('accounts/login/', LoginView.as_view(), name='account_login'),
    path('accounts/signup/', SignupView.as_view(), name='account_signup'),
    path('accounts/logout/', LogoutView.as_view(), name='account_logout'),
    
    # Include core URLs
    path('', include('core.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
