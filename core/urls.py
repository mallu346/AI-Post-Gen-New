from django.urls import path
from django.shortcuts import redirect
from . import views

# Simple redirect functions
def redirect_to_allauth_login(request):
    return redirect('/accounts/login/')

def redirect_to_allauth_signup(request):
    return redirect('/accounts/signup/')

def redirect_to_allauth_logout(request):
    return redirect('/accounts/logout/')

urlpatterns = [
    # Home and main pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('explore/', views.explore, name='explore'),
    
    # User-related pages
    path('generate/', views.generate_image_view, name='generate_image'),
    path('gallery/', views.gallery, name='gallery'),
    path('profile/', views.profile_redirect, name='profile'),
    path('profile/<str:username>/', views.profile, name='user_profile'),
    
    # Image management URLs
    path('image/download/<uuid:image_id>/', views.download_image, name='download_image'),
    path('image/delete/<uuid:image_id>/', views.delete_image, name='delete_image'),
    path('image/share/<uuid:image_id>/', views.share_image, name='share_image'),
    path('image/<uuid:image_id>/', views.image_share_view, name='image_share_view'),
    path('image/toggle-privacy/<uuid:image_id>/', views.toggle_image_privacy, name='toggle_image_privacy'),
    path('images/bulk-delete/', views.bulk_delete_images, name='bulk_delete_images'),
    
    # QR Code generation URL
    path('qr-code/<uuid:image_id>/', views.generate_qr_code_view, name='generate_qr_code'),
    
    # Post-related pages
    path('post/<uuid:pk>/', views.post_detail, name='post_detail'),
    
    # Redirect old authentication URLs to allauth (optional, for backward compatibility)
    path('signup/', redirect_to_allauth_signup, name='signup'),
    path('login/', redirect_to_allauth_login, name='login'),
    path('logout/', redirect_to_allauth_logout, name='logout'),
]
