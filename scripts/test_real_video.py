#!/usr/bin/env python3
"""
Test script for REAL AI video generation
Run this to test if real video generation is working
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_social_platform.settings')
django.setup()

from utils.real_video_generator import generate_real_ai_video

def test_real_video_generation():
    """Test real AI video generation"""
    
    print("🧪 TESTING REAL AI VIDEO GENERATION")
    print("=" * 50)
    
    test_prompts = [
        "a cat walking",
        "bird flying in sky", 
        "ocean waves",
        "fire burning",
        "clouds moving"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n🎬 Test {i}/5: '{prompt}'")
        print("-" * 30)
        
        try:
            video_file, thumbnail_file, source, metadata = generate_real_ai_video(
                prompt=prompt,
                duration=3,
                quality='draft',
                fps=12,
                seed=42
            )
            
            if video_file:
                print(f"✅ SUCCESS! Generated with {source}")
                print(f"📁 Size: {metadata.get('file_size', 'unknown')} bytes")
                print(f"🏷️ Service: {metadata.get('service', 'unknown')}")
                return True  # Success on first working prompt
            else:
                print(f"❌ Failed to generate video")
        
        except Exception as e:
            print(f"💥 Exception: {str(e)}")
    
    print(f"\n❌ All test prompts failed")
    return False

if __name__ == "__main__":
    success = test_real_video_generation()
    if success:
        print(f"\n🎉 REAL AI video generation is working!")
    else:
        print(f"\n😞 REAL AI video generation needs setup")
        print(f"\n💡 Next steps:")
        print(f"1. Get a free Hugging Face token: https://huggingface.co/settings/tokens")
        print(f"2. Add to settings: HUGGINGFACE_API_TOKEN = 'your_token'")
        print(f"3. Try Replicate free tier: https://replicate.com/")
