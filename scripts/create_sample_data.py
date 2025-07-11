#!/usr/bin/env python3
"""
Create sample data for testing the video generation system
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import VideoStylePreset, GeneratedVideo
from utils.video_generator import VideoHashtagGenerator

User = get_user_model()

def create_sample_video_presets():
    """Create additional sample video style presets"""
    print("🎨 Creating sample video style presets...")
    
    advanced_presets = [
        {
            'name': 'Drone Shot',
            'description': 'Aerial perspective with smooth drone-like camera movements',
            'prompt_suffix': ', aerial drone shot, bird\'s eye view, smooth camera movement, cinematic',
            'category': 'cinematic',
            'is_active': True
        },
        {
            'name': 'Macro Close-up',
            'description': 'Extreme close-up with shallow depth of field',
            'prompt_suffix': ', macro photography, extreme close-up, shallow depth of field, detailed',
            'category': 'cinematic',
            'is_active': True
        },
        {
            'name': 'Slow Motion',
            'description': 'Dramatic slow-motion effect for impactful scenes',
            'prompt_suffix': ', slow motion, dramatic timing, high frame rate, smooth movement',
            'category': 'cinematic',
            'is_active': True
        },
        {
            'name': 'Pixel Art',
            'description': '8-bit retro gaming style with pixelated animation',
            'prompt_suffix': ', pixel art style, 8-bit, retro gaming, pixelated animation',
            'category': 'animation',
            'is_active': True
        },
        {
            'name': 'Oil Painting',
            'description': 'Classical oil painting style with rich textures',
            'prompt_suffix': ', oil painting style, classical art, rich textures, painterly',
            'category': 'artistic',
            'is_active': True
        }
    ]
    
    created_count = 0
    for preset_data in advanced_presets:
        preset, created = VideoStylePreset.objects.get_or_create(
            name=preset_data['name'],
            defaults=preset_data
        )
        if created:
            created_count += 1
            print(f"  ✅ Created: {preset.name}")
    
    print(f"🎨 Created {created_count} additional video style presets!")

def create_sample_videos():
    """Create sample video records for testing"""
    print("🎬 Creating sample video records...")
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='video_test_user',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Video',
            'last_name': 'Tester'
        }
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"  ✅ Created test user: {user.username}")
    
    # Sample video prompts
    sample_prompts = [
        "A majestic dragon flying over a medieval castle at sunset",
        "Ocean waves crashing against rocky cliffs in slow motion",
        "A bustling cyberpunk city street with neon lights at night",
        "Colorful autumn leaves falling in a peaceful forest",
        "A time-lapse of clouds moving over mountain peaks",
        "Abstract geometric shapes morphing and changing colors",
        "A cute robot walking through a futuristic laboratory",
        "Underwater scene with tropical fish swimming around coral reefs"
    ]
    
    # Get some style presets
    style_presets = list(VideoStylePreset.objects.all()[:4])
    
    created_count = 0
    for i, prompt in enumerate(sample_prompts):
        # Generate hashtags for the prompt
        style_preset = style_presets[i % len(style_presets)] if style_presets else None
        hashtags = VideoHashtagGenerator.generate_video_hashtags(
            prompt, 
            style_preset.category if style_preset else None
        )
        
        video, created = GeneratedVideo.objects.get_or_create(
            user=user,
            prompt=prompt,
            defaults={
                'video_style_preset': style_preset,
                'duration': [3, 5, 10][i % 3],
                'quality': ['draft', 'standard', 'high'][i % 3],
                'fps': [12, 24, 30][i % 3],
                'status': ['pending', 'processing', 'completed', 'failed'][i % 4],
                'generation_source': 'mock',
                'hashtags': ', '.join(hashtags),
                'is_public': True
            }
        )
        
        if created:
            created_count += 1
            print(f"  ✅ Created sample video: {prompt[:50]}...")
    
    print(f"🎬 Created {created_count} sample video records!")

def main():
    """Main function to create sample data"""
    print("📊 Creating Sample Data for Video Generation")
    print("=" * 50)
    
    try:
        create_sample_video_presets()
        create_sample_videos()
        
        print("\n🎉 Sample data creation complete!")
        print("=" * 50)
        print("✅ Additional video style presets created")
        print("✅ Sample video records created")
        print("✅ Test user created (username: video_test_user, password: testpass123)")
        
        print("\n🔗 You can now:")
        print("1. Login with the test user to see sample videos")
        print("2. Test the video generation system")
        print("3. View the video gallery with sample data")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
