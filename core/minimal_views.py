from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import os
import uuid
from datetime import datetime

from .forms import CustomUserCreationForm, ImageGenerationForm
from .services.huggingface_service import generate_image
from .file_storage import file_storage

def home(request):
    """Simple homepage."""
    # Get recent generations from file storage
    recent_images = []
    if request.user.is_authenticated:
        user_generations = file_storage.get_user_generations(request.user.id)
        recent_images = user_generations[-6:]  # Last 6 images
    
    return render(request, 'core/simple_home.html', {
        'recent_images': recent_images
    })

def signup(request):
    """User registration."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def generate_image_view(request):
    """AI image generation with file storage."""
    if request.method == 'POST':
        form = ImageGenerationForm(request.POST)
        if form.is_valid():
            try:
                # Generate image
                image, content_file = generate_image(
                    prompt=form.cleaned_data['prompt'],
                    width=int(form.cleaned_data.get('width', 512)),
                    height=int(form.cleaned_data.get('height', 512))
                )
                
                if image and content_file:
                    # Save image to media folder
                    filename = f"{uuid.uuid4()}.png"
                    image_path = os.path.join('media', 'generated_images', filename)
                    
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(image_path), exist_ok=True)
                    
                    # Save image file
                    with open(image_path, 'wb') as f:
                        f.write(content_file.read())
                    
                    # Log generation to file storage
                    file_storage.save_generation_log(
                        user_id=request.user.id,
                        prompt=form.cleaned_data['prompt'],
                        image_path=image_path
                    )
                    
                    messages.success(request, 'Image generated successfully!')
                    return redirect('gallery')
                else:
                    messages.error(request, 'Failed to generate image.')
            
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
    else:
        form = ImageGenerationForm()
    
    return render(request, 'core/generate.html', {'form': form})

@login_required
def gallery(request):
    """User's personal gallery from file storage."""
    user_generations = file_storage.get_user_generations(request.user.id)
    
    # Convert file paths to URLs
    for generation in user_generations:
        generation['image_url'] = '/' + generation['image_path'].replace('\\', '/')
    
    return render(request, 'core/gallery.html', {
        'generations': user_generations
    })

@login_required
def preferences(request):
    """User preferences stored in files."""
    if request.method == 'POST':
        prefs = {
            'theme': request.POST.get('theme', 'light'),
            'default_style': request.POST.get('default_style', ''),
            'image_size': request.POST.get('image_size', '512'),
        }
        file_storage.save_user_preferences(request.user.id, prefs)
        messages.success(request, 'Preferences saved!')
        return redirect('preferences')
    
    user_prefs = file_storage.get_user_preferences(request.user.id)
    return render(request, 'core/preferences.html', {
        'preferences': user_prefs
    })
