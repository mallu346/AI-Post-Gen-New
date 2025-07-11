#!/usr/bin/env python3
"""
Fix API token configuration and test real video generation
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_social_platform.settings')
django.setup()

from django.conf import settings

def check_api_tokens():
    """Check and validate API tokens"""
    
    print("🔑 CHECKING API TOKEN CONFIGURATION")
    print("=" * 50)
    
    tokens = {
        'HUGGINGFACE_API_TOKEN': getattr(settings, 'HUGGINGFACE_API_TOKEN', ''),
        'REPLICATE_API_TOKEN': getattr(settings, 'REPLICATE_API_TOKEN', ''),
        'FAL_API_KEY': getattr(settings, 'FAL_API_KEY', ''),
        'RUNWAY_API_KEY': getattr(settings, 'RUNWAY_API_KEY', ''),
    }
    
    valid_tokens = {}
    
    for token_name, token_value in tokens.items():
        print(f"\n🔍 Checking {token_name}:")
        
        if not token_value or token_value.strip() == '':
            print(f"  ❌ Not configured")
            continue
        
        if token_value in ['your_token_here', 'your_key_here']:
            print(f"  ❌ Default placeholder value")
            continue
        
        # Basic validation
        token_clean = token_value.strip()
        
        if token_name == 'HUGGINGFACE_API_TOKEN':
            if token_clean.startswith('hf_') and len(token_clean) > 10:
                print(f"  ✅ Valid format: {token_clean[:10]}...")
                valid_tokens[token_name] = token_clean
            else:
                print(f"  ⚠️ Invalid format (should start with 'hf_')")
        
        elif token_name == 'REPLICATE_API_TOKEN':
            if token_clean.startswith('r8_') and len(token_clean) > 10:
                print(f"  ✅ Valid format: {token_clean[:10]}...")
                valid_tokens[token_name] = token_clean
            else:
                print(f"  ⚠️ Invalid format (should start with 'r8_')")
        
        elif token_name == 'FAL_API_KEY':
            if len(token_clean) > 10:
                print(f"  ✅ Configured: {token_clean[:10]}...")
                valid_tokens[token_name] = token_clean
            else:
                print(f"  ⚠️ Too short")
        
        elif token_name == 'RUNWAY_API_KEY':
            if len(token_clean) > 10:
                print(f"  ✅ Configured: {token_clean[:10]}...")
                valid_tokens[token_name] = token_clean
            else:
                print(f"  ⚠️ Too short")
    
    print(f"\n📊 SUMMARY:")
    print(f"Valid tokens: {len(valid_tokens)}/4")
    
    if len(valid_tokens) == 0:
        print(f"\n❌ NO VALID TOKENS FOUND!")
        print_setup_instructions()
        return False
    
    elif len(valid_tokens) >= 1:
        print(f"\n✅ At least one valid token found!")
        test_tokens(valid_tokens)
        return True
    
    return False

def print_setup_instructions():
    """Print setup instructions for API tokens"""
    
    print(f"\n🛠️ SETUP INSTRUCTIONS:")
    print("=" * 50)
    
    print(f"\n1. 🤗 HUGGING FACE (FREE):")
    print(f"   • Go to: https://huggingface.co/settings/tokens")
    print(f"   • Sign up/login")
    print(f"   • Click 'New token' → 'Read' access")
    print(f"   • Copy token (starts with 'hf_')")
    print(f"   • Add to settings.py: HUGGINGFACE_API_TOKEN = 'hf_your_token'")
    
    print(f"\n2. 🔄 REPLICATE (FREE TIER):")
    print(f"   • Go to: https://replicate.com/account/api-tokens")
    print(f"   • Sign up/login")
    print(f"   • Create API token")
    print(f"   • Copy token (starts with 'r8_')")
    print(f"   • Add to settings.py: REPLICATE_API_TOKEN = 'r8_your_token'")
    
    print(f"\n3. 🚀 FAL.AI (FREE TIER):")
    print(f"   • Go to: https://fal.ai/dashboard")
    print(f"   • Sign up/login")
    print(f"   • Get API key")
    print(f"   • Add to settings.py: FAL_API_KEY = 'your_key'")
    
    print(f"\n💡 QUICK START:")
    print(f"   Just get the Hugging Face token - it's free and works!")

def test_tokens(valid_tokens):
    """Test the valid tokens"""
    
    print(f"\n🧪 TESTING VALID TOKENS:")
    print("=" * 50)
    
    if 'HUGGINGFACE_API_TOKEN' in valid_tokens:
        test_huggingface_token(valid_tokens['HUGGINGFACE_API_TOKEN'])
    
    if 'REPLICATE_API_TOKEN' in valid_tokens:
        test_replicate_token(valid_tokens['REPLICATE_API_TOKEN'])

def test_huggingface_token(token):
    """Test Hugging Face token"""
    
    print(f"\n🤗 Testing Hugging Face token...")
    
    try:
        import requests
        
        # Test with a simple model
        url = "https://api-inference.huggingface.co/models/gpt2"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"inputs": "Hello"}
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        print(f"  📊 Response: {response.status_code}")
        
        if response.status_code == 200:
            print(f"  ✅ Token is VALID and working!")
            return True
        elif response.status_code == 401:
            print(f"  ❌ Token is INVALID or expired")
            return False
        else:
            print(f"  ⚠️ Unexpected response: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"  ❌ Test failed: {str(e)}")
        return False

def test_replicate_token(token):
    """Test Replicate token"""
    
    print(f"\n🔄 Testing Replicate token...")
    
    try:
        import requests
        
        # Test by listing models
        url = "https://api.replicate.com/v1/models"
        headers = {"Authorization": f"Token {token}"}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"  📊 Response: {response.status_code}")
        
        if response.status_code == 200:
            print(f"  ✅ Token is VALID and working!")
            return True
        elif response.status_code == 401:
            print(f"  ❌ Token is INVALID or expired")
            return False
        else:
            print(f"  ⚠️ Unexpected response: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"  ❌ Test failed: {str(e)}")
        return False

def main():
    """Main function"""
    
    print("🔧 API TOKEN FIXER")
    print("=" * 50)
    
    success = check_api_tokens()
    
    if success:
        print(f"\n🎉 READY FOR REAL AI VIDEO GENERATION!")
        print(f"Now try generating a video in your Django app.")
    else:
        print(f"\n⚠️ SETUP REQUIRED")
        print(f"Follow the instructions above to get API tokens.")
    
    return success

if __name__ == "__main__":
    main()
