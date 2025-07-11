#!/usr/bin/env python3
"""
Setup script for AI Video Generation features
Run this after adding the video generation code to your Django project
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_social_platform.settings')
    django.setup()

def run_migrations():
    """Run database migrations for new video models"""
    print("🔄 Running database migrations...")
    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'makemigrations'])
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Database migrations completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def create_video_style_presets():
    """Create default video style presets"""
    
    from core.models import VideoStylePreset
    
    presets = [
        {
            'name': 'Cinematic',
            'description': 'Professional movie-like quality with dramatic lighting and camera movements',
            'prompt_suffix': ', cinematic lighting, professional cinematography, film grain, dramatic composition',
            'category': 'cinematic'
        },
        {
            'name': 'Animation',
            'description': 'Smooth animated style perfect for cartoon-like videos',
            'prompt_suffix': ', smooth animation, cartoon style, vibrant colors, animated movement',
            'category': 'animation'
        },
        {
            'name': 'Nature Documentary',
            'description': 'Natural, organic movements with realistic lighting',
            'prompt_suffix': ', natural lighting, organic movement, documentary style, realistic',
            'category': 'nature'
        },
        {
            'name': 'Abstract Art',
            'description': 'Surreal and artistic with flowing, abstract movements',
            'prompt_suffix': ', abstract art, surreal movement, artistic composition, flowing motion',
            'category': 'abstract'
        },
        {
            'name': 'Retro Vintage',
            'description': 'Nostalgic vintage style with retro color grading',
            'prompt_suffix': ', vintage style, retro color grading, nostalgic atmosphere, film aesthetic',
            'category': 'artistic'
        },
        {
            'name': 'Sci-Fi Future',
            'description': 'Futuristic style with neon lights and high-tech elements',
            'prompt_suffix': ', futuristic, neon lights, high-tech, sci-fi atmosphere, cyberpunk',
            'category': 'cinematic'
        },
        {
            'name': 'Dreamy Ethereal',
            'description': 'Soft, dreamy quality with ethereal lighting and gentle movements',
            'prompt_suffix': ', dreamy atmosphere, ethereal lighting, soft focus, gentle movement',
            'category': 'artistic'
        },
        {
            'name': 'Action Dynamic',
            'description': 'High-energy with fast movements and dynamic camera work',
            'prompt_suffix': ', dynamic movement, fast-paced, action sequence, energetic',
            'category': 'cinematic'
        }
    ]
    
    created_count = 0
    for preset_data in presets:
        preset, created = VideoStylePreset.objects.get_or_create(
            name=preset_data['name'],
            defaults=preset_data
        )
        if created:
            created_count += 1
            print(f"✅ Created video style preset: {preset.name}")
        else:
            print(f"⚠️  Video style preset already exists: {preset.name}")
    
    print(f"\n🎬 Video style presets setup complete! Created {created_count} new presets.")
    return created_count

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    print("🎬 Checking FFmpeg installation...")
    
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"  ✅ FFmpeg found: {version_line}")
            return True
        else:
            print("  ❌ FFmpeg not working properly")
            return False
    except FileNotFoundError:
        print("  ❌ FFmpeg not found")
        return False
    except Exception as e:
        print(f"  ❌ Error checking FFmpeg: {e}")
        return False

def install_ffmpeg_instructions():
    """Provide FFmpeg installation instructions"""
    print("\n📋 FFmpeg Installation Instructions:")
    print("=" * 50)
    
    print("\n🐧 Ubuntu/Debian:")
    print("sudo apt update && sudo apt install ffmpeg")
    
    print("\n🍎 macOS (with Homebrew):")
    print("brew install ffmpeg")
    
    print("\n🪟 Windows:")
    print("1. Download from: https://ffmpeg.org/download.html")
    print("2. Extract to C:\\ffmpeg")
    print("3. Add C:\\ffmpeg\\bin to your PATH")
    print("4. Or use Chocolatey: choco install ffmpeg")
    
    print("\n🐳 Docker:")
    print("docker run --rm -v $(pwd):/workspace jrottenberg/ffmpeg")
    
    print("\n📝 Note: FFmpeg is optional but recommended for better mock video generation")

def create_superuser_if_needed():
    """Create superuser if none exists"""
    print("👤 Checking for superuser...")
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if not User.objects.filter(is_superuser=True).exists():
        print("  ⚠️  No superuser found. You'll need one to access Django admin.")
        print("  Run: python manage.py createsuperuser")
    else:
        print("  ✅ Superuser exists")

def test_video_generation():
    """Test the video generation system"""
    print("🧪 Testing video generation system...")
    
    try:
        from utils.video_generator import generate_ai_video
        
        # Test with a simple prompt
        test_prompt = "A beautiful sunset over mountains"
        print(f"  Testing with prompt: '{test_prompt}'")
        
        video_file, thumbnail_file, source, metadata = generate_ai_video(
            prompt=test_prompt,
            duration=3,
            quality='draft',
            fps=12
        )
        
        if video_file:
            print(f"  ✅ Video generation test successful! Source: {source}")
            print(f"  📁 Video file size: {len(video_file.read())} bytes")
            return True
        else:
            print("  ❌ Video generation test failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Video generation test error: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up video generation features...\n")
    
    # Setup Django
    setup_django()
    
    try:
        # Step 1: Run migrations
        if not run_migrations():
            print("❌ Setup failed at migration step")
            return False
        
        # Step 2: Create video style presets
        create_video_style_presets()
        
        # Step 3: Check FFmpeg
        ffmpeg_available = check_ffmpeg()
        if not ffmpeg_available:
            install_ffmpeg_instructions()
        
        # Step 4: Check superuser
        create_superuser_if_needed()
        
        # Step 5: Test video generation
        test_video_generation()
        
        print("\n✅ Video features setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Add your API keys to settings.py or .env file:")
        print("   - RUNWAY_API_KEY (for Runway ML)")
        print("   - REPLICATE_API_TOKEN (for Replicate)")
        print("   - HUGGINGFACE_API_TOKEN (for Hugging Face)")
        print("2. Run migrations: python manage.py makemigrations && python manage.py migrate")
        print("3. Start generating videos!")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
