from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
import json
import os
import mimetypes
from urllib.parse import quote
import random # Add this import

# QR Code imports
import qrcode
from io import BytesIO
import base64
from PIL import Image

from .models import CustomUser, Post, GeneratedImage, StylePreset, Like, Comment
from .forms import (
    CustomUserCreationForm, ProfileUpdateForm, ImageGenerationForm, CommentForm, PostForm
)
from .hashtag_generator import HashtagGenerator

import requests # Ensure this is imported at the top of the file
from requests.exceptions import RequestException, Timeout, HTTPError # Add these imports

def home(request):
    """Homepage with trending posts and interactive features"""
    # Get recent posts with images
    posts = GeneratedImage.objects.filter(is_public=True).order_by('-created_at')[:12]

    # Get some stats
    total_users = CustomUser.objects.count()
    total_images = GeneratedImage.objects.count()
    total_posts = GeneratedImage.objects.filter(is_public=True).count()

    # Get active style presets for the styles modal
    style_presets = StylePreset.objects.filter(is_active=True)

    context = {
        'page_title': 'AI Social Media Platform',
        'posts': posts,
        'total_users': total_users,
        'total_images': total_images,
        'total_posts': total_posts,
        'style_presets': style_presets,
    }
    return render(request, 'core/home.html', context)

@login_required
def generate_image_view(request):
    """AI image generation page with style preselection and hashtag generation"""
    form = ImageGenerationForm() # Initialize form for GET requests or invalid POST

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
                
                # Clear previous API errors from session
                request.session.pop('hf_error', None)
                request.session.pop('pollinations_error', None)

                # Try multiple free services in order and track which one works
                image_content, source, metadata = generate_image_free_services_with_tracking(request, prompt, style_suffix) # Pass request object
                
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
                    
                    # Generate hashtags
                    try:
                        hashtags = HashtagGenerator.generate_hashtags(
                            prompt=prompt,
                            style_preset=style_preset.name if style_preset else None,
                            max_hashtags=15
                        )
                        
                        # Save hashtags to the model
                        generated_image.set_hashtags_list(hashtags)
                        generated_image.save(update_fields=['hashtags'])
                        
                        print(f"✅ Generated {len(hashtags)} hashtags for image")
                    except Exception as hashtag_error:
                        print(f"⚠️ Hashtag generation failed: {hashtag_error}")
                        # Continue without hashtags if generation fails
                        
                    print(f"💾 Saved image from {source} to database with ID: {generated_image.id}")
                    service_name = metadata.get('service_name', source)
                    
                    # Show different messages based on service used
                    if source == 'mock':
                        messages.warning(request, f'Image generated using fallback generator. External AI services may be temporarily unavailable.')
                        # Add specific API errors if they occurred
                        if request.session.get('hf_error'):
                            messages.error(request, f"Hugging Face API failed: {request.session.pop('hf_error')}")
                        if request.session.get('pollinations_error'):
                            messages.error(request, f"Pollinations AI failed: {request.session.pop('pollinations_error')}")
                    else:
                        messages.success(request, f'Image generated successfully using {service_name}! 🎨')
                    
                    return redirect('post_detail', pk=generated_image.id)
                else:
                    print("❌ Image generation returned None")
                    messages.error(request, 'Failed to generate image. Please try again.')
            
            except Exception as e:
                print(f"💥 Exception in generate_image_view: {e}")
                messages.error(request, f'Error generating image: {str(e)}')
                # The function will now fall through to render the form again with the error message
        else:
            # Form is not valid, messages will be handled by Django's form rendering
            messages.error(request, 'Please correct the errors in the form.')
            # The function will now fall through to render the form again with validation errors

    # This part handles both initial GET requests and POST requests where generation failed or form was invalid
    style_presets = StylePreset.objects.filter(is_active=True)
    trending_hashtags = HashtagGenerator.get_trending_hashtags()

    context = {
        'form': form,
        'style_presets': style_presets,
        'trending_hashtags': trending_hashtags,
        'page_title': 'Generate AI Image'
    }
    return render(request, 'core/generate.html', context)

def generate_image_free_services_with_tracking(request, prompt, style_suffix=""):
    """Try multiple free AI image generation services with source tracking"""
    full_prompt = f"{prompt}{style_suffix}" if style_suffix else prompt

    print(f"🎨 Starting free image generation for: {full_prompt}")

    # PRIORITY 1: Hugging Face Spaces (Free)
    try:
        print("🤗 Trying Hugging Face Spaces (Priority 1)...")
        image_content = generate_with_hf_spaces_improved(full_prompt)
        if image_content:
            metadata = {
                "service_name": "Hugging Face Spaces",
                "service_url": "https://huggingface.co/",
                "cost": "Free",
                "model": "runwayml/stable-diffusion-v1-5",
                "prompt": full_prompt,
                "timestamp": timezone.now().isoformat(),
                "reliability": "High",
                "priority": 1
            }
            print("✅ Hugging Face image generated successfully!")
            return image_content, 'huggingface', metadata
    except Exception as e:
        error_message = f"Hugging Face failed: {e}"
        print(f"❌ {error_message}")
        # Store the specific error for later use in messages
        request.session['hf_error'] = str(e) # Use request.session to pass error

    # PRIORITY 2: Pollinations AI (Fallback)
    try:
        print("🌸 Trying Pollinations AI (Fallback)...")
        image_content = generate_with_pollinations(full_prompt)
        if image_content:
            metadata = {
                "service_name": "Pollinations AI",
                "service_url": "https://pollinations.ai/",
                "cost": "Free",
                "prompt": full_prompt,
                "timestamp": timezone.now().isoformat(),
                "reliability": "Medium",
                "priority": 2
            }
            print("✅ Pollinations image generated successfully!")
            return image_content, 'pollinations', metadata
    except Exception as e:
        error_message = f"Pollinations failed: {e}"
        print(f"❌ {error_message}")
        # Store the specific error for later use in messages
        request.session['pollinations_error'] = str(e) # Use request.session to pass error

    # FINAL FALLBACK: Enhanced Mock Generator
    print("🎭 Using enhanced mock generator...")
    image_content = generate_enhanced_mock_image(full_prompt)
    metadata = {
        "service_name": "Enhanced Mock Generator",
        "service_url": "Local fallback",
        "cost": "Free (local)",
        "note": "Fallback when all external APIs are unavailable",
        "prompt": full_prompt,
        "timestamp": timezone.now().isoformat(),
        "reliability": "Fallback",
        "priority": 3
    }
    return image_content, 'mock', metadata

def generate_with_hf_spaces_improved(prompt):
    """IMPROVED Hugging Face Spaces generation with better error handling"""
    try:
        from django.core.files.base import ContentFile
        import time

        print("🤗 Trying IMPROVED Hugging Face Spaces...")

        # Changed to a more robust Stable Diffusion XL model
        api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

        headers = {
            "Authorization": f"Bearer {settings.HUGGINGFACE_API_TOKEN}", # Use token from settings
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": prompt,
            "parameters": {
                "num_inference_steps": 25,
                "guidance_scale": 7.5,
                "width": 1024, # SDXL models typically work better with larger dimensions
                "height": 1024,
                "negative_prompt": "blurry, bad quality, distorted, ugly, low resolution, extra limbs, deformed, malformed"
            },
            "options": {
                "wait_for_model": True,
                "use_cache": False
            }
        }

        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=90
        )

        print(f"📡 HF Response status: {response.status_code}")

        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'image' in content_type:
                image_content = ContentFile(response.content, name=f'hf_{prompt[:20]}.png')
                print("✅ Hugging Face image generated successfully!")
                return image_content
            else:
                error_detail = response.text[:200] if response.text else "No content"
                raise Exception(f"Hugging Face returned non-image content or empty response: {error_detail}")

        elif response.status_code == 503:
            print("⏳ HF Model loading, waiting 10 seconds...")
            time.sleep(10)
            # Retry once
            response = requests.post(api_url, headers=headers, json=payload, timeout=90)
            if response.status_code == 200 and 'image' in response.headers.get('content-type', ''):
                image_content = ContentFile(response.content, name=f'hf_{prompt[:20]}.png')
                print("✅ Hugging Face image generated successfully on retry!")
                return image_content
            else:
                error_detail = response.text[:200] if response.text else "No content on retry"
                raise Exception(f"Hugging Face API failed on retry (Status: {response.status_code}): {error_detail}")

        else:
            error_detail = response.text[:200] if response.text else "Unknown error"
            raise Exception(f"Hugging Face API returned unexpected status {response.status_code}: {error_detail}")

    except Timeout:
        raise Exception("Hugging Face API timed out. The model might be busy or slow.")
    except HTTPError as e:
        raise Exception(f"Hugging Face API HTTP error: {e.response.status_code} - {e.response.text[:200]}")
    except RequestException as e:
        raise Exception(f"Hugging Face API network error: {str(e)}")
    except Exception as e:
        raise Exception(f"Hugging Face Spaces failed: {str(e)}")

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
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        if response.content:
            image_content = ContentFile(response.content, name=f'pollinations_{prompt[:20]}.png')
            print("✅ Pollinations image generated successfully!")
            return image_content
        else:
            raise Exception("Pollinations API returned no image content.")

    except Timeout:
        raise Exception("Pollinations AI API timed out. The service might be busy or slow.")
    except HTTPError as e:
        raise Exception(f"Pollinations AI API HTTP error: {e.response.status_code} - {e.response.text[:200]}")
    except RequestException as e:
        raise Exception(f"Pollinations AI API network error: {str(e)}")
    except Exception as e:
        raise Exception(f"Pollinations API failed: {str(e)}")

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

        # Add "AI GENERATED" watermark
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
            draw.ellipse([x-size//2, y-size//2, x+size//2, y+size//2], 
                        fill=color, outline=None)

def add_styled_text(draw, width, height, prompt):
    """Add styled text to the image"""
    try:
        font_size = 28
        font = ImageFont.load_default()
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
        watermark_font = ImageFont.load_default()
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

@login_required
def download_image(request, image_id):
    """Download an image file"""
    try:
        image = get_object_or_404(GeneratedImage, id=image_id)
        
        # Check permissions
        if not image.is_public and image.user != request.user:
            if not request.user.is_authenticated:
                messages.error(request, 'Please log in to download this image.')
                return redirect('account_login')
            else:
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
        
        # Determine content type
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = 'image/png'
        
        # Read the file
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Create HTTP response with proper headers
        response = HttpResponse(file_data, content_type=content_type)
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
        image = get_object_or_404(GeneratedImage, id=image_id, user=request.user)
        
        if request.method == 'POST':
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
    """Share image view with QR code support"""
    try:
        image = get_object_or_404(GeneratedImage, id=image_id)
        
        # Check if image is accessible
        if not image.is_public and (not request.user.is_authenticated or image.user != request.user):
            if not request.user.is_authenticated:
                messages.error(request, 'This image is private. Please log in to download this image.')
                return redirect('account_login')
            else:
                messages.error(request, 'This image is private.')
                return redirect('explore')
        
        # Build the full share URL for QR code
        share_url = request.build_absolute_uri(
            reverse('image_share_view', kwargs={'image_id': image.id})
        )
        
        # Get related images from same user (public only)
        related_images = GeneratedImage.objects.filter(
            user=image.user, 
            is_public=True
        ).exclude(id=image.id).order_by('-created_at')[:6]
        
        context = {
            'image': image,
            'related_images': related_images,
            'share_url': share_url,
            'page_title': f'Share: {image.prompt[:50]}...'
        }
        return render(request, 'core/share_image.html', context)
        
    except Exception as e:
        print(f"❌ Share error: {e}")
        raise Http404("Image not found")

def image_share_view(request, image_id):
    """Public view for shared images"""
    try:
        image = get_object_or_404(GeneratedImage, id=image_id)
        
        # Check if image is public or user owns it
        if not image.is_public and (not request.user.is_authenticated or image.user != request.user):
            if not request.user.is_authenticated:
                messages.error(request, 'This image is private. Please log in if you have access.')
                return redirect('account_login')
            else:
                messages.error(request, 'This image is private.')
                return redirect('explore')
        
        # Get related images from the same user
        related_images = GeneratedImage.objects.filter(
            user=image.user,
            is_public=True
        ).exclude(id=image.id)[:3]
        
        context = {
            'image': image,
            'related_images': related_images,
            'page_title': f'{image.prompt[:50]}...'
        }
        
        return render(request, 'core/image_share_view.html', context)
        
    except Exception as e:
        print(f"❌ Image share view error: {e}")
        raise Http404("Image not found")

def generate_qr_code_view(request, image_id):
    """Generate QR code for image sharing"""
    try:
        image = get_object_or_404(GeneratedImage, id=image_id)
        
        # Check if image is accessible
        if not image.is_public and (not request.user.is_authenticated or image.user != request.user):
            return JsonResponse({'error': 'Image not accessible'}, status=403)
        
        # Build the share URL
        share_url = request.build_absolute_uri(
            reverse('image_share_view', kwargs={'image_id': image.id})
        )
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(share_url)
        qr.make(fit=True)
        
        # Create QR code image
        qr_image = qr.make_image(fill_color="#0d6efd", back_color="white")
        
        # Convert to base64 for embedding in HTML
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        print(f"✅ QR code generated for image {image_id}")
        
        return JsonResponse({
            'success': True,
            'qr_code': f'data:image/png;base64,{qr_base64}',
            'share_url': share_url
        })
        
    except Exception as e:
        print(f"❌ QR generation error: {e}")
        return JsonResponse({'error': 'Failed to generate QR code'}, status=500)

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

def post_detail(request, pk):
    """Post detail page with hashtags"""
    try:
        print(f"🔍 Looking for image with ID: {pk}")
        
        try:
            image = GeneratedImage.objects.get(id=pk)
            print(f"✅ Found image: {image.prompt[:50]}... by {image.user.username}")
        except GeneratedImage.DoesNotExist:
            print(f"❌ Image with ID {pk} does not exist")
            recent_images = GeneratedImage.objects.filter(is_public=True).order_by('-created_at')[:5]
            context = {
                'error_message': f'Image with ID {pk} was not found.',
                'suggested_images': recent_images,
                'page_title': 'Image Not Found'
            }
            return render(request, 'core/image_not_found.html', context)
        
        # Check if image is accessible
        if not image.is_public:
            if not request.user.is_authenticated:
                print(f"❌ Private image, user not authenticated")
                raise Http404("Image not found or not accessible")
            elif image.user != request.user:
                print(f"❌ Private image, user {request.user.username} is not owner {image.user.username}")
                raise Http404("Image not found or not accessible")
        
        print(f"✅ Image is accessible to user")
        
        # Get related images from same user (public only)
        related_images = GeneratedImage.objects.filter(
            user=image.user, 
            is_public=True
        ).exclude(id=image.id).order_by('-created_at')[:6]
        
        print(f"📸 Found {related_images.count()} related images")
        
        context = {
            'image': image,
            'related_images': related_images,
            'page_title': f'Image: {image.prompt[:50]}...'
        }
        return render(request, 'core/post_detail.html', context)
        
    except Http404:
        raise
    except Exception as e:
        print(f"❌ Unexpected error in post_detail: {e}")
        import traceback
        traceback.print_exc()
        
        context = {
            'error_message': 'An unexpected error occurred while loading this image.',
            'page_title': 'Error'
        }
        return render(request, 'core/image_not_found.html', context)

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
