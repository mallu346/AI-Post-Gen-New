"""
AI Video Generation Utilities - Updated to use WORKING services
"""

from typing import Dict, Any, Optional, Tuple
import os
import requests
import tempfile
import subprocess
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils import timezone
import json
import time
import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import hashlib
import math

# Import the working video generator
from .working_video_generator import generate_working_ai_video

class VideoHashtagGenerator:
    """Generate hashtags for videos"""
    
    @staticmethod
    def generate_video_hashtags(prompt, style=None, max_hashtags=15):
        """Generate relevant hashtags for video content"""
        
        # Base video hashtags
        base_hashtags = [
            '#AIVideo', '#GeneratedVideo', '#ArtificialIntelligence', 
            '#VideoArt', '#DigitalArt', '#AIGenerated'
        ]
        
        # Style-specific hashtags
        style_hashtags = {
            'cinematic': ['#Cinematic', '#FilmStyle', '#MovieMagic', '#CinematicAI'],
            'animation': ['#Animation', '#AnimatedVideo', '#CartoonStyle', '#MotionGraphics'],
            'abstract': ['#AbstractArt', '#SurrealVideo', '#ArtisticVideo', '#AbstractAnimation'],
            'nature': ['#NatureVideo', '#Documentary', '#NaturalMotion', '#Organic'],
            'artistic': ['#ArtVideo', '#CreativeVideo', '#VisualArt', '#ArtisticExpression']
        }
        
        # Content-based hashtags from prompt
        content_hashtags = []
        prompt_lower = prompt.lower()
        
        # Analyze prompt for relevant hashtags
        keyword_map = {
            'cat': ['#Cat', '#Pet', '#Animal', '#Feline'],
            'dog': ['#Dog', '#Pet', '#Animal', '#Canine'],
            'walk': ['#Walking', '#Movement', '#Motion'],
            'run': ['#Running', '#Fast', '#Action'],
            'fly': ['#Flying', '#Sky', '#Birds', '#Flight'],
            'swim': ['#Swimming', '#Water', '#Ocean'],
            'sunset': ['#Sunset', '#GoldenHour', '#Sky'],
            'ocean': ['#Ocean', '#Water', '#Waves', '#Sea'],
            'mountain': ['#Mountains', '#Landscape', '#Nature'],
            'city': ['#City', '#Urban', '#Cityscape'],
            'space': ['#Space', '#Galaxy', '#Stars', '#Cosmos'],
            'forest': ['#Forest', '#Trees', '#Woods', '#Green'],
            'fire': ['#Fire', '#Flames', '#Heat'],
            'dance': ['#Dance', '#Movement', '#Motion'],
            'music': ['#Music', '#Sound', '#Audio'],
            'love': ['#Love', '#Romance', '#Heart'],
            'dream': ['#Dream', '#Surreal', '#Fantasy'],
            'future': ['#Future', '#SciFi', '#Technology'],
            'vintage': ['#Vintage', '#Retro', '#Classic'],
            'magic': ['#Magic', '#Fantasy', '#Mystical']
        }
        
        for keyword, hashtags in keyword_map.items():
            if keyword in prompt_lower:
                content_hashtags.extend(hashtags)
        
        # Combine all hashtags
        all_hashtags = base_hashtags.copy()
        
        # Add style hashtags
        if style and style in style_hashtags:
            all_hashtags.extend(style_hashtags[style])
        
        # Add content hashtags
        all_hashtags.extend(content_hashtags)
        
        # Remove duplicates and limit
        unique_hashtags = list(dict.fromkeys(all_hashtags))
        
        # Add some trending video hashtags
        trending = ['#VideoOfTheDay', '#AIArt', '#TechArt', '#Innovation', '#Creative']
        unique_hashtags.extend(trending)
        
        # Remove duplicates again and limit to max_hashtags
        final_hashtags = list(dict.fromkeys(unique_hashtags))[:max_hashtags]
        
        return final_hashtags

def generate_ai_video(prompt, duration=5, quality='standard', fps=24, seed=None):
    """
    Main video generation function - now uses WORKING AI services
    """
    print(f"\n🎬 STARTING WORKING AI VIDEO GENERATION")
    print("=" * 60)
    print(f"📝 Prompt: {prompt}")
    print(f"⏱️ Duration: {duration}s")
    print(f"🎯 Quality: {quality}")
    print(f"🎞️ FPS: {fps}")
    print(f"🎲 Seed: {seed}")
    print("=" * 60)
    
    try:
        # Use the working AI video generator
        video_file, thumbnail_file, source, metadata = generate_working_ai_video(
            prompt=prompt,
            duration=duration,
            quality=quality,
            fps=fps,
            seed=seed
        )
        
        if video_file:
            print(f"\n✅ SUCCESS! Working AI video generated!")
            print(f"🏷️ Source: {source}")
            print(f"📁 File size: {metadata.get('file_size', 'unknown')} bytes")
            print(f"🎬 Service: {metadata.get('service', 'unknown')}")
            print("=" * 60)
            
            return video_file, thumbnail_file, source, metadata
        else:
            print(f"\n❌ FAILED! No video generated")
            print("Falling back to enhanced mock generation...")
            print("=" * 60)
            
            # Fallback to enhanced mock
            return generate_enhanced_mock_video(prompt, duration, quality, fps, seed)
    
    except Exception as e:
        print(f"\n💥 EXCEPTION in video generation: {str(e)}")
        print("Falling back to enhanced mock generation...")
        print("=" * 60)
        
        # Fallback to enhanced mock
        return generate_enhanced_mock_video(prompt, duration, quality, fps, seed)

def generate_enhanced_mock_video(prompt, duration, quality, fps, seed):
    """
    Generate an enhanced mock video that's better than before
    """
    print(f"🎭 Generating ENHANCED mock video for: {prompt}")
    
    try:
        # Check if FFmpeg is available for better mock videos
        if check_ffmpeg():
            return generate_ffmpeg_enhanced_mock(prompt, duration, quality, fps, seed)
        else:
            return generate_animated_mock_video(prompt, duration, quality, fps, seed)
    
    except Exception as e:
        print(f"❌ Enhanced mock generation failed: {e}")
        return generate_simple_mock_video(prompt, duration, quality, fps, seed)

def generate_animated_mock_video(prompt, duration, quality, fps, seed):
    """
    Generate an animated mock video (multiple frames as GIF)
    """
    print("🎨 Creating animated mock video...")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Set up parameters
        if seed:
            random.seed(seed)
        else:
            seed = random.randint(1, 1000000)
            random.seed(seed)
        
        size_map = {
            'draft': (480, 360),
            'standard': (640, 480),
            'high': (1280, 720)
        }
        width, height = size_map.get(quality, (640, 480))
        
        # Create multiple frames for animation
        frame_count = min(duration * fps, 30)  # Max 30 frames
        frames = []
        
        print(f"  🎞️ Creating {frame_count} frames at {width}x{height}")
        
        for i in range(frame_count):
            frame = create_enhanced_animated_frame(prompt, i, frame_count, width, height, seed)
            frames.append(frame)
        
        # Save as animated GIF
        gif_io = BytesIO()
        frames[0].save(
            gif_io,
            format='GIF',
            save_all=True,
            append_images=frames[1:],
            duration=int(1000/fps),  # Duration per frame in ms
            loop=0
        )
        
        video_file = ContentFile(gif_io.getvalue(), name=f'enhanced_mock_{prompt[:20]}.gif')
        
        # Create thumbnail from first frame
        thumb_io = BytesIO()
        frames[0].save(thumb_io, format='JPEG', quality=85)
        thumbnail_file = ContentFile(thumb_io.getvalue(), name=f'enhanced_thumb_{prompt[:20]}.jpg')
        
        metadata = {
            'service': 'Enhanced Mock Generator (Animated)',
            'quality': quality,
            'duration': duration,
            'fps': fps,
            'resolution': f'{width}x{height}',
            'frames': frame_count,
            'format': 'GIF',
            'file_size': len(gif_io.getvalue()),
            'seed': seed,
            'note': 'This is an enhanced animated mock video. Get API keys for real AI videos.'
        }
        
        print(f"  ✅ Enhanced animated mock created! Size: {len(gif_io.getvalue())} bytes")
        
        return video_file, thumbnail_file, metadata
    
    except Exception as e:
        print(f"❌ Animated mock failed: {e}")
        return generate_simple_mock_video(prompt, duration, quality, fps, seed)

def create_enhanced_animated_frame(prompt, frame_num, total_frames, width, height, seed):
    """
    Create an enhanced animated frame with better visuals
    """
    # Create base image
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    
    # Animation progress
    progress = frame_num / max(total_frames - 1, 1)
    
    # Generate theme colors based on prompt
    colors = get_enhanced_theme_colors(prompt, seed)
    
    # Create animated background
    create_enhanced_animated_background(draw, width, height, colors, progress)
    
    # Add animated elements based on prompt
    add_prompt_based_elements(draw, width, height, colors, progress, prompt)
    
    # Add text overlay
    add_enhanced_text_overlay(draw, width, height, prompt, frame_num, total_frames)
    
    return image

def get_enhanced_theme_colors(prompt, seed):
    """
    Get enhanced theme colors based on prompt analysis
    """
    random.seed(seed)
    prompt_lower = prompt.lower()
    
    # Analyze prompt for color themes
    if any(word in prompt_lower for word in ['cat', 'orange', 'warm']):
        return [(255, 140, 0), (255, 165, 0), (255, 69, 0)]  # Orange theme
    elif any(word in prompt_lower for word in ['ocean', 'blue', 'water', 'sky']):
        return [(30, 144, 255), (0, 191, 255), (135, 206, 235)]  # Blue theme
    elif any(word in prompt_lower for word in ['forest', 'green', 'nature', 'tree']):
        return [(34, 139, 34), (0, 128, 0), (50, 205, 50)]  # Green theme
    elif any(word in prompt_lower for word in ['fire', 'red', 'hot']):
        return [(255, 69, 0), (255, 0, 0), (220, 20, 60)]  # Red theme
    elif any(word in prompt_lower for word in ['space', 'galaxy', 'stars', 'night']):
        return [(25, 25, 112), (72, 61, 139), (123, 104, 238)]  # Purple theme
    else:
        # Dynamic colors based on prompt hash
        prompt_hash = hash(prompt) % 1000
        random.seed(prompt_hash)
        return [
            (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
            for _ in range(3)
        ]

def create_enhanced_animated_background(draw, width, height, colors, progress):
    """
    Create an enhanced animated background with gradients and movement
    """
    # Create moving gradient
    for y in range(height):
        # Add wave motion to the gradient
        wave_offset = math.sin((y / height * 4 + progress * 2) * math.pi) * 0.2
        ratio = (y / height + wave_offset + progress * 0.3) % 1.0
        
        # Interpolate between colors
        color_index = int(ratio * (len(colors) - 1))
        next_index = (color_index + 1) % len(colors)
        local_ratio = (ratio * (len(colors) - 1)) - color_index
        
        r = int(colors[color_index][0] * (1 - local_ratio) + colors[next_index][0] * local_ratio)
        g = int(colors[color_index][1] * (1 - local_ratio) + colors[next_index][1] * local_ratio)
        b = int(colors[color_index][2] * (1 - local_ratio) + colors[next_index][2] * local_ratio)
        
        draw.line([(0, y), (width, y)], fill=(r, g, b))

def add_prompt_based_elements(draw, width, height, colors, progress, prompt):
    """
    Add animated elements based on the prompt content
    """
    prompt_lower = prompt.lower()
    
    # Add different elements based on prompt
    if 'cat' in prompt_lower:
        add_cat_elements(draw, width, height, colors, progress)
    elif any(word in prompt_lower for word in ['bird', 'fly']):
        add_flying_elements(draw, width, height, colors, progress)
    elif any(word in prompt_lower for word in ['ocean', 'wave']):
        add_wave_elements(draw, width, height, colors, progress)
    elif 'fire' in prompt_lower:
        add_fire_elements(draw, width, height, colors, progress)
    else:
        add_generic_elements(draw, width, height, colors, progress)

def add_cat_elements(draw, width, height, colors, progress):
    """Add cat-themed animated elements"""
    # Animated cat silhouette
    cat_x = int(width * 0.2 + (width * 0.6) * progress)
    cat_y = int(height * 0.7)
    
    # Simple cat shape
    # Body
    draw.ellipse([cat_x, cat_y, cat_x + 60, cat_y + 30], fill=colors[0])
    # Head
    draw.ellipse([cat_x + 45, cat_y - 20, cat_x + 75, cat_y + 10], fill=colors[0])
    # Ears
    draw.polygon([(cat_x + 50, cat_y - 15), (cat_x + 55, cat_y - 25), (cat_x + 60, cat_y - 15)], fill=colors[0])
    draw.polygon([(cat_x + 65, cat_y - 15), (cat_x + 70, cat_y - 25), (cat_x + 75, cat_y - 15)], fill=colors[0])
    # Tail
    tail_curve = int(10 * math.sin(progress * 4 * math.pi))
    draw.ellipse([cat_x - 15, cat_y + 10 + tail_curve, cat_x + 5, cat_y + 20 + tail_curve], fill=colors[0])

def add_flying_elements(draw, width, height, colors, progress):
    """Add flying bird elements"""
    # Multiple birds flying
    for i in range(3):
        bird_x = int((width * 0.1 + i * width * 0.3) + (width * 0.4) * progress)
        bird_y = int(height * 0.3 + i * 50 + 20 * math.sin(progress * 3 * math.pi + i))
        
        # Simple bird shape (V)
        wing_span = 15 + int(5 * math.sin(progress * 8 * math.pi + i))
        draw.line([(bird_x - wing_span, bird_y), (bird_x, bird_y - 10), (bird_x + wing_span, bird_y)], 
                 fill=colors[i % len(colors)], width=3)

def add_wave_elements(draw, width, height, colors, progress):
    """Add ocean wave elements"""
    # Animated waves
    for i in range(5):
        wave_y = height * 0.6 + i * 20
        for x in range(0, width, 10):
            wave_height = 10 * math.sin((x / 50 + progress * 2 + i) * math.pi)
            y = int(wave_y + wave_height)
            draw.ellipse([x, y, x + 8, y + 8], fill=colors[i % len(colors)])

def add_fire_elements(draw, width, height, colors, progress):
    """Add fire flame elements"""
    # Animated flames
    flame_base_y = int(height * 0.8)
    for i in range(7):
        flame_x = width * 0.3 + i * 20
        flame_height = 40 + 20 * math.sin(progress * 6 * math.pi + i)
        flame_y = flame_base_y - flame_height
        
        # Flame shape
        points = [
            (flame_x, flame_base_y),
            (flame_x - 8, flame_y + 20),
            (flame_x, flame_y),
            (flame_x + 8, flame_y + 20)
        ]
        draw.polygon(points, fill=colors[i % len(colors)])

def add_generic_elements(draw, width, height, colors, progress):
    """Add generic animated elements"""
    # Floating particles
    num_particles = 12
    for i in range(num_particles):
        angle = (i / num_particles) * 2 * math.pi + progress * 2 * math.pi
        radius = 100 + 50 * math.sin(progress * 3 * math.pi + i)
        
        x = int(width / 2 + radius * math.cos(angle))
        y = int(height / 2 + radius * math.sin(angle))
        
        size = 8 + int(4 * math.sin(progress * 4 * math.pi + i))
        draw.ellipse([x - size, y - size, x + size, y + size], fill=colors[i % len(colors)])

def add_enhanced_text_overlay(draw, width, height, prompt, frame_num, total_frames):
    """Add enhanced text overlay with animation"""
    try:
        font = ImageFont.load_default()
        
        # Main prompt text with animation
        words = prompt.split()
        if len(words) > 8:
            text_lines = [' '.join(words[:8]), ' '.join(words[8:])]
        else:
            text_lines = [prompt]
        
        # Animated text position
        text_alpha = int(200 + 55 * math.sin(frame_num / total_frames * 2 * math.pi))
        
        y_offset = height // 2 - len(text_lines) * 25
        for line in text_lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            
            # Animated background
            bg_expand = int(10 * math.sin(frame_num / total_frames * 4 * math.pi))
            draw.rectangle([x - 25 - bg_expand, y_offset - 15, 
                          x + text_width + 25 + bg_expand, y_offset + 35], 
                         fill=(0, 0, 0, 180))
            
            # Text with glow effect
            for offset in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                draw.text((x + offset[0], y_offset + offset[1]), line, fill=(100, 100, 100), font=font)
            draw.text((x, y_offset), line, fill='white', font=font)
            
            y_offset += 50
        
        # Frame counter
        frame_text = f"Frame {frame_num + 1}/{total_frames}"
        draw.text((20, height - 40), frame_text, fill='white', font=font)
        
        # Enhanced watermark
        watermark = "ENHANCED AI MOCK VIDEO"
        bbox = draw.textbbox((0, 0), watermark, font=font)
        watermark_width = bbox[2] - bbox[0]
        draw.rectangle([width - watermark_width - 30, 10, width - 10, 35], fill=(0, 0, 0, 150))
        draw.text((width - watermark_width - 20, 15), watermark, fill='white', font=font)
        
    except Exception as e:
        print(f"⚠️ Enhanced text overlay failed: {e}")

def check_ffmpeg():
    """Check if FFmpeg is available"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
        return True
    except:
        return False

def generate_simple_mock_video(prompt, duration, quality, fps, seed):
    """Fallback simple mock video"""
    print("🎭 Creating simple mock video (fallback)...")
    
    # Create a single frame
    size_map = {
        'draft': (480, 360),
        'standard': (640, 480), 
        'high': (1280, 720)
    }
    width, height = size_map.get(quality, (640, 480))
    
    if seed:
        random.seed(seed)
    else:
        seed = random.randint(1, 1000000)
        random.seed(seed)
    
    # Create simple frame
    frame = create_enhanced_animated_frame(prompt, 0, 1, width, height, seed)
    
    # Save as image
    img_io = BytesIO()
    frame.save(img_io, format='PNG', quality=95)
    
    video_file = ContentFile(img_io.getvalue(), name=f'simple_mock_{prompt[:20]}.png')
    
    # Create thumbnail
    thumb_io = BytesIO()
    frame.save(thumb_io, format='JPEG', quality=85)
    thumbnail_file = ContentFile(thumb_io.getvalue(), name=f'simple_thumb_{prompt[:20]}.jpg')
    
    metadata = {
        'service': 'Simple Mock Generator',
        'quality': quality,
        'duration': duration,
        'fps': fps,
        'resolution': f'{width}x{height}',
        'file_size': len(img_io.getvalue()),
        'seed': seed,
        'note': 'Simple mock video. Set up API keys for real AI videos.'
    }
    
    return video_file, thumbnail_file, metadata
