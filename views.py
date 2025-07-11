from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
import json
import os
import mimetypes
from urllib.parse import quote

from .models import CustomUser, Post, GeneratedImage, StylePreset, Like, Comment
from .forms import (
    CustomUserCreationForm, ProfileUpdateForm, ImageGenerationForm, CommentForm, PostForm
)

def home(request):
    """Homepage with trending posts"""
    # Get recent posts with images
    posts = GeneratedImage.objects.filter(is_public=True).order_by('-created_at')[:12]
    
    # Get some stats
    total_users = CustomUser.objects.count()
    total_images = GeneratedImage.objects.count()
    total_posts = GeneratedImage.objects.filter(is_public=True).count()
    
    context = {
        'page_title': 'AI Social Media Platform',
        'posts': posts,
        'total_users': total_users,
        'total_images': total_images,
        'total_posts': total_posts,
    }
    return render(request, 'core/home.html', context)

@login_required
def generate_image_view(request):
    """AI image generation page"""
    if request.method == 'POST':
        form = ImageGenerationForm(request.POST)
        if form.is_valid():
            try:
                # Get form data
                prompt = form.cleaned_data['prompt']
                style_preset = form.cleaned_data['style_preset']
                width = int(form.cleaned_data.get('width', 512))
                height = int(form.cleaned_data.get('height', 512))
                seed = form.cleaned_data.get('seed')
                
                # Get style suffix
                style_suffix = ""
                if style_preset:
                    style_suffix = style_preset.prompt_suffix
                
                print(f"🎯 Form data - Prompt: {prompt}, Style: {style_preset}")
                
                # Show loading message
                messages.info(request, 'Generating your AI image... This may take a few moments.')
                
                # Try multiple free services in order and track which one works
                image_content, source, metadata = generate_image_free_services_with_tracking(prompt, style_suffix)
                
                if image_content:
                    # Create GeneratedImage record with source tracking
                    generated_image = GeneratedImage.objects.create(
                        user=request.user,
                        prompt=prompt,
                        style_preset=style_preset,
                        seed=seed,
                        width=width,
                        height=height,
                        is_public=True,
                        generation_source=source,
                        generation_metadata=metadata
                    )
                    
                    # Save the image file
                    generated_image.image.save(
                        f'generated_{generated_image.id}.png',
                        image_content,
                        save=True
                    )
                    
                    print(f"💾 Saved image from {source} to database with ID: {generated_image.id}")
                    service_name = metadata.get('service_name', source)
                    
                    # Show different messages based on service used
                    if source == 'mock':
                        messages.warning(request, f'Image generated using fallback generator. External AI services may be temporarily unavailable.')
                    else:
                        messages.success(request, f'Image generated successfully using {service_name}! 🎨')
                    
                    return redirect('gallery')
                else:
                    print("❌ Image generation returned None")
                    messages.error(request, 'Failed to generate image. Please try again.')
            
            except Exception as e:
                print(f"💥 Exception in generate_image_view: {e}")
                messages.error(request, f'Error generating image: {str(e)}')
                
    else:
        form = ImageGenerationForm()
    
    # Get active style presets for the template
    style_presets = StylePreset.objects.filter(is_active=True)
    
    context = {
        'form': form,
        'style_presets': style_presets,
        'page_title': 'Generate AI Image'
    }
    return render(request, 'core/generate.html', context)

@login_required
def download_image(request, image_id):
    """Download an image file"""
    try:
        # Get the image - user can download their own images or public images
        image = get_object_or_404(GeneratedImage, id=image_id)
        
        # Check permissions
        if not image.is_public and image.user != request.user:
            messages.error(request, "You don't have permission to download this image.")
            return redirect('gallery')
        
        # Check if image file exists
        if not image.image or not os.path.exists(image.image.path):
            messages.error(request, "Image file not found.")
            return redirect('gallery')
        
        # Prepare the file for download
        file_path = image.image.path
        file_name = f"ai_generated_{image.prompt[:30].replace(' ', '_')}_{str(image.id)[:8]}.png"
        
        # Clean filename for download
        file_name = "".join(c for c in file_name if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
        
        # Read the file
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Create HTTP response
        response = HttpResponse(file_data, content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        response['Content-Length'] = len(file_data)
        
        print(f"📥 User {request.user.username} downloaded image {image.id}")
        return response
        
    except Exception as e:
        print(f"❌ Download error: {e}")
        messages.error(request, "Error downloading image. Please try again.")
        return redirect('gallery')

@login_required
def delete_image(request, image_id):
    """Delete an image"""
    try:
        # Get the image - only owner can delete
        image = get_object_or_404(GeneratedImage, id=image_id, user=request.user)
        
        if request.method == 'POST':
            # Store image info for success message
            prompt = image.prompt[:50]
            
            # Delete the image file from filesystem
            if image.image and os.path.exists(image.image.path):
                try:
                    os.remove(image.image.path)
                    print(f"🗑️ Deleted image file: {image.image.path}")
                except Exception as e:
                    print(f"⚠️ Could not delete file: {e}")
            
            # Delete the database record
            image.delete()
            
            messages.success(request, f'Image "{prompt}..." has been deleted successfully.')
            print(f"🗑️ User {request.user.username} deleted image {image_id}")
            
            return redirect('gallery')
        
        # GET request - show confirmation page
        context = {
            'image': image,
            'page_title': 'Delete Image'
        }
        return render(request, 'core/delete_image.html', context)
        
    except Exception as e:
        print(f"❌ Delete error: {e}")
        messages.error(request, "Error deleting image. Please try again.")
        return redirect('gallery')

def share_image(request, image_id):
    """Share an image - public view"""
    try:
        # Get public image or user's own image
        image = get_object_or_404(GeneratedImage, id=image_id)
        
        # Check if image is accessible
        if not image.is_public and (not request.user.is_authenticated or image.user != request.user):
            raise Http404("Image not found or not accessible")
        
        # Get related images from same user (public only)
        related_images = GeneratedImage.objects.filter(
            user=image.user, 
            is_public=True
        ).exclude(id=image.id).order_by('-created_at')[:6]
        
        # Build share URLs
        share_url = request.build_absolute_uri()
        
        context = {
            'image': image,
            'related_images': related_images,
            'share_url': share_url,
            'page_title': f'Shared Image: {image.prompt[:50]}...'
        }
        return render(request, 'core/share_image.html', context)
        
    except Exception as e:
        print(f"❌ Share error: {e}")
        raise Http404("Image not found")

@login_required
@require_POST
def toggle_image_privacy(request, image_id):
    """Toggle image privacy (public/private)"""
    try:
        image = get_object_or_404(GeneratedImage, id=image_id, user=request.user)
        
        # Toggle privacy
        image.is_public = not image.is_public
        image.save(update_fields=['is_public'])
        
        status = "public" if image.is_public else "private"
        messages.success(request, f'Image is now {status}.')
        
        return JsonResponse({
            'success': True,
            'is_public': image.is_public,
            'status': status
        })
        
    except Exception as e:
        print(f"❌ Privacy toggle error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to update privacy setting'
        })

@login_required
@require_POST
def bulk_delete_images(request):
    """Delete multiple images at once"""
    try:
        image_ids = request.POST.getlist('image_ids')
        
        if not image_ids:
            messages.error(request, "No images selected for deletion.")
            return redirect('gallery')
        
        # Get user's images only
        images = GeneratedImage.objects.filter(id__in=image_ids, user=request.user)
        
        if not images.exists():
            messages.error(request, "No valid images found for deletion.")
            return redirect('gallery')
        
        deleted_count = 0
        for image in images:
            # Delete file from filesystem
            if image.image and os.path.exists(image.image.path):
                try:
                    os.remove(image.image.path)
                except Exception as e:
                    print(f"⚠️ Could not delete file: {e}")
            
            # Delete database record
            image.delete()
            deleted_count += 1
        
        messages.success(request, f'Successfully deleted {deleted_count} image(s).')
        print(f"🗑️ User {request.user.username} bulk deleted {deleted_count} images")
        
        return redirect('gallery')
        
    except Exception as e:
        print(f"❌ Bulk delete error: {e}")
        messages.error(request, "Error deleting images. Please try again.")
        return redirect('gallery')

def generate_image_free_services_with_tracking(prompt, style_suffix=""):
    """Try multiple free AI image generation services with source tracking"""
    full_prompt = f"{prompt}{style_suffix}" if style_suffix else prompt
    
    print(f"🎨 Starting free image generation for: {full_prompt}")
    
    # Try Method 1: Pollinations AI (Completely Free)
    try:
        image_content = generate_with_pollinations(full_prompt)
        if image_content:
            metadata = {
                "service_name": "Pollinations AI",
                "service_url": "https://pollinations.ai/",
                "cost": "Free",
                "prompt": full_prompt,
                "timestamp": timezone.now().isoformat(),
                "reliability": "High"
            }
            return image_content, 'pollinations', metadata
    except Exception as e:
        print(f"❌ Pollinations failed: {e}")
    
    # Try Method 2: Hugging Face Spaces (Free)
    try:
        image_content = generate_with_hf_spaces(full_prompt)
        if image_content:
            metadata = {
                "service_name": "Hugging Face Spaces",
                "service_url": "https://huggingface.co/",
                "cost": "Free",
                "model": "runwayml/stable-diffusion-v1-5",
                "prompt": full_prompt,
                "timestamp": timezone.now().isoformat(),
                "reliability": "Medium"
            }
            return image_content, 'huggingface', metadata
    except Exception as e:
        print(f"❌ HF Spaces failed: {e}")
    
    # Try Method 3: DeepAI (Free tier)
    try:
        image_content = generate_with_deepai(full_prompt)
        if image_content:
            metadata = {
                "service_name": "DeepAI",
                "service_url": "https://deepai.org/",
                "cost": "Free tier",
                "prompt": full_prompt,
                "timestamp": timezone.now().isoformat(),
                "reliability": "Low"
            }
            return image_content, 'deepai', metadata
    except Exception as e:
        print(f"❌ DeepAI failed: {e}")
    
    # Fallback: Enhanced Mock Generator
    print("🎭 Using enhanced mock generator...")
    image_content = generate_enhanced_mock_image(full_prompt)
    metadata = {
        "service_name": "Enhanced Mock Generator",
        "service_url": "Local fallback",
        "cost": "Free (local)",
        "note": "Fallback when all external APIs are unavailable",
        "prompt": full_prompt,
        "timestamp": timezone.now().isoformat(),
        "reliability": "Fallback"
    }
    return image_content, 'mock', metadata

# Keep all existing generation functions the same...
def generate_image_free_services(prompt, style_suffix=""):
    """Original function for backward compatibility"""
    image_content, source, metadata = generate_image_free_services_with_tracking(prompt, style_suffix)
    return image_content

def generate_with_pollinations(prompt):
    """Generate image using Pollinations AI (Free)"""
    try:
        import requests
        from django.core.files.base import ContentFile
        import urllib.parse
        
        print("🌸 Trying Pollinations AI...")
        
        # Pollinations API endpoint
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&seed=42"
        
        print(f"📡 Calling: {url}")
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        if response.content:
            image_content = ContentFile(response.content, name=f'pollinations_{prompt[:20]}.png')
            print("✅ Pollinations image generated successfully!")
            return image_content
        else:
            raise Exception("No content received")
            
    except Exception as e:
        raise Exception(f"Pollinations API failed: {str(e)}")

def generate_with_hf_spaces(prompt):
    """Generate image using Hugging Face Spaces (Free)"""
    try:
        import requests
        from django.core.files.base import ContentFile
        
        print("🤗 Trying Hugging Face Spaces...")
        
        # Use a public Stable Diffusion space
        api_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        
        headers = {
            "Authorization": "Bearer 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"  # Your HF token
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "num_inference_steps": 20,
                "guidance_scale": 7.5
            }
        }
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            image_content = ContentFile(response.content, name=f'hf_{prompt[:20]}.png')
            print("✅ Hugging Face image generated successfully!")
            return image_content
        else:
            raise Exception(f"HF API returned {response.status_code}")
            
    except Exception as e:
        raise Exception(f"Hugging Face Spaces failed: {str(e)}")

def generate_with_deepai(prompt):
    """Generate image using DeepAI (Free tier)"""
    try:
        import requests
        from django.core.files.base import ContentFile
        
        print("🧠 Trying DeepAI...")
        
        # DeepAI API (has free tier)
        api_url = "https://api.deepai.org/api/text2img"
        
        response = requests.post(
            api_url,
            data={'text': prompt},
            headers={'api-key': 'quickstart-QUdJIGlzIGNvbWluZy4uLi4K'}  # Free tier key
        )
        
        if response.status_code == 200:
            result = response.json()
            image_url = result.get('output_url')
            
            if image_url:
                # Download the image
                img_response = requests.get(image_url, timeout=30)
                img_response.raise_for_status()
                
                image_content = ContentFile(img_response.content, name=f'deepai_{prompt[:20]}.png')
                print("✅ DeepAI image generated successfully!")
                return image_content
            else:
                raise Exception("No image URL in response")
        else:
            raise Exception(f"DeepAI API returned {response.status_code}")
            
    except Exception as e:
        raise Exception(f"DeepAI failed: {str(e)}")

def generate_enhanced_mock_image(prompt):
    """Generate an enhanced mock image with better design"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        from django.core.files.base import ContentFile
        import io
        import random
        import hashlib
        
        print(f"🎭 Generating enhanced mock for: {prompt}")
        
        # Create a unique seed from prompt for consistent results
        seed = int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16)
        random.seed(seed)
        
        # Create image
        width, height = 512, 512
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)
        
        # Generate theme-based colors based on prompt keywords
        colors = get_theme_colors(prompt)
        
        # Create artistic background
        create_artistic_background(draw, width, height, colors)
        
        # Add decorative elements
        add_decorative_elements(draw, width, height, colors, prompt)
        
        # Add prompt text with better styling
        add_styled_text(draw, width, height, prompt)
        
        # Add "AI GENERATED" watermark instead of "MOCK"
        add_watermark(draw, width, height)
        
        # Convert to bytes
        img_io = io.BytesIO()
        image.save(img_io, format='PNG', quality=95)
        img_io.seek(0)
        
        print("✅ Enhanced mock image generated!")
        return ContentFile(img_io.getvalue(), name=f'enhanced_mock_{prompt[:20]}.png')
        
    except Exception as e:
        print(f"Mock generation error: {e}")
        # Return simple fallback
        from PIL import Image
        import io
        image = Image.new('RGB', (512, 512), color=(100, 150, 200))
        img_io = io.BytesIO()
        image.save(img_io, format='PNG')
        img_io.seek(0)
        return ContentFile(img_io.getvalue(), name='simple_fallback.png')

def get_theme_colors(prompt):
    """Get colors based on prompt keywords"""
    prompt_lower = prompt.lower()
    
    if any(word in prompt_lower for word in ['sunset', 'orange', 'warm']):
        return [(255, 165, 0), (255, 69, 0), (255, 140, 0)]  # Orange theme
    elif any(word in prompt_lower for word in ['ocean', 'blue', 'water', 'sky']):
        return [(30, 144, 255), (0, 191, 255), (135, 206, 235)]  # Blue theme
    elif any(word in prompt_lower for word in ['forest', 'green', 'nature']):
        return [(34, 139, 34), (0, 128, 0), (50, 205, 50)]  # Green theme
    elif any(word in prompt_lower for word in ['purple', 'magic', 'fantasy']):
        return [(138, 43, 226), (147, 112, 219), (186, 85, 211)]  # Purple theme
    else:
        return [(255, 107, 107), (78, 205, 196), (69, 183, 209)]  # Default

def create_artistic_background(draw, width, height, colors):
    """Create an artistic gradient background"""
    for y in range(height):
        # Create a complex gradient
        ratio = y / height
        color_index = int(ratio * (len(colors) - 1))
        next_index = min(color_index + 1, len(colors) - 1)
        
        local_ratio = (ratio * (len(colors) - 1)) - color_index
        
        r = int(colors[color_index][0] * (1 - local_ratio) + colors[next_index][0] * local_ratio)
        g = int(colors[color_index][1] * (1 - local_ratio) + colors[next_index][1] * local_ratio)
        b = int(colors[color_index][2] * (1 - local_ratio) + colors[next_index][2] * local_ratio)
        
        draw.line([(0, y), (width, y)], fill=(r, g, b))

def add_decorative_elements(draw, width, height, colors, prompt):
    """Add decorative elements based on prompt"""
    prompt_lower = prompt.lower()
    
    # Add stars for space/night themes
    if any(word in prompt_lower for word in ['space', 'night', 'star', 'galaxy']):
        for _ in range(30):
            x, y = random.randint(0, width), random.randint(0, height)
            size = random.randint(2, 6)
            draw.ellipse([x-size, y-size, x+size, y+size], fill='white')
    
    # Add circles for abstract themes
    else:
        for _ in range(15):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(20, 80)
            color = random.choice(colors)
            alpha_color = color + (random.randint(50, 150),)
            draw.ellipse([x-size//2, y-size//2, x+size//2, y+size//2], 
                        fill=color, outline=None)

def add_styled_text(draw, width, height, prompt):
    """Add styled text to the image"""
    try:
        font_size = 28
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Wrap text nicely
    words = prompt.split()
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        line_text = ' '.join(current_line)
        bbox = draw.textbbox((0, 0), line_text, font=font)
        if bbox[2] > width - 60:  # 30px margin on each side
            if len(current_line) > 1:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(word)
                current_line = []
    
    if current_line:
        lines.append(' '.join(current_line))
    
    # Draw text with nice styling
    y_offset = height // 2 - (len(lines) * 35) // 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        
        # Draw shadow
        draw.text((x+2, y_offset+2), line, fill=(0, 0, 0, 100), font=font)
        
        # Draw text background
        draw.rectangle([x-15, y_offset-8, x+text_width+15, y_offset+30], 
                      fill=(255, 255, 255, 200))
        
        # Draw main text
        draw.text((x, y_offset), line, fill=(50, 50, 50), font=font)
        y_offset += 35

def add_watermark(draw, width, height):
    """Add AI GENERATED watermark"""
    try:
        watermark_font = ImageFont.truetype("arial.ttf", 36)
    except:
        watermark_font = ImageFont.load_default()
    
    watermark_text = "AI GENERATED"
    bbox = draw.textbbox((0, 0), watermark_text, font=watermark_font)
    watermark_width = bbox[2] - bbox[0]
    watermark_x = width - watermark_width - 20
    watermark_y = height - 50
    
    # Draw watermark with background
    draw.rectangle([watermark_x-10, watermark_y-5, watermark_x+watermark_width+10, watermark_y+35], 
                  fill=(0, 0, 0, 150))
    draw.text((watermark_x, watermark_y), watermark_text, fill='white', font=watermark_font)

# ... (rest of your existing views remain the same)

@login_required
def gallery(request):
    """User's personal gallery with source information"""
    # Get user's generated images
    images = GeneratedImage.objects.filter(user=request.user).order_by('-created_at')
    
    # Calculate stats
    total_images = images.count()
    total_views = 0  # We'll implement view tracking later
    total_likes = 0  # We'll implement this when we add the Like system
    public_posts = images.filter(is_public=True).count()
    
    # Add service stats
    service_stats = {}
    for image in images:
        source = image.generation_source
        if source not in service_stats:
            service_stats[source] = {
                'count': 0,
                'display_name': image.get_service_display_name()
            }
        service_stats[source]['count'] += 1
    
    context = {
        'images': images,
        'total_images': total_images,
        'total_views': total_views,
        'total_likes': total_likes,
        'public_posts': public_posts,
        'service_stats': service_stats,
        'page_title': 'My Gallery'
    }
    return render(request, 'core/gallery.html', context)

def explore(request):
    """Explore page"""
    posts = GeneratedImage.objects.filter(is_public=True).order_by('-created_at')
    
    context = {
        'page_title': 'Explore',
        'posts': posts
    }
    return render(request, 'core/explore.html', context)

def about(request):
    """About page"""
    context = {
        'page_title': 'About'
    }
    return render(request, 'core/about.html', context)

@login_required
def profile_redirect(request):
    """Redirect to user's own profile"""
    return redirect('user_profile', username=request.user.username)

def profile(request, username):
    """User profile page"""
    user = get_object_or_404(CustomUser, username=username)
    
    # Get user's images
    images = GeneratedImage.objects.filter(user=user, is_public=True).order_by('-created_at')[:6]
    total_images = GeneratedImage.objects.filter(user=user, is_public=True).count()
    
    context = {
        'profile_user': user,
        'images': images,
        'total_images': total_images,
        'page_title': f"{user.username}'s Profile"
    }
    return render(request, 'core/profile.html', context)

def feedback(request):
    """Feedback page"""
    context = {
        'page_title': 'Feedback'
    }
    return render(request, 'core/feedback.html', context)

def post_detail(request, pk):
    """Post detail page - placeholder for now"""
    context = {
        'page_title': 'Post Detail'
    }
    return render(request, 'core/post_detail.html', context)

@login_required
@require_POST
def toggle_like(request, post_id):
    """Toggle like on a post"""
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'like_count': post.likes.count()
    })

def signup(request):
    """User registration"""
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
