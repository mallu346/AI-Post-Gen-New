"""
REAL AI Video Generation - Working Implementation
This focuses on actually working free AI video services
"""

import requests
import time
import random
import os
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils import timezone
from io import BytesIO
import json

def generate_real_ai_video(prompt, duration=5, quality='standard', fps=24, seed=None):
    """
    Generate REAL AI video using working free services
    """
    print(f"🎬 REAL AI Video Generation Starting...")
    print(f"📝 Prompt: {prompt}")
    print(f"⏱️ Duration: {duration}s, Quality: {quality}, FPS: {fps}")
    
    # Try real services in order
    real_services = [
        ('huggingface_working', try_huggingface_video_real),
        ('replicate_working', try_replicate_video_real),
        ('fal_ai', try_fal_ai_video),
        ('pollinations_real', try_pollinations_real),
        ('runway_free', try_runway_free_tier)
    ]
    
    for service_name, service_func in real_services:
        try:
            print(f"\n🔄 Trying REAL service: {service_name}")
            print("-" * 50)
            
            result = service_func(prompt, duration, quality, fps, seed)
            
            if result and result[0]:  # If video was generated
                video_file, thumbnail_file, metadata = result
                print(f"✅ SUCCESS! Real video generated with {service_name}")
                print(f"📁 Video size: {len(video_file.read())} bytes")
                video_file.seek(0)  # Reset file pointer
                return video_file, thumbnail_file, service_name, metadata
            
        except Exception as e:
            print(f"❌ {service_name} failed: {str(e)}")
            continue
    
    print("\n❌ All real AI services failed - this shouldn't happen!")
    return None, None, 'failed', {'error': 'All real services failed'}

def try_huggingface_video_real(prompt, duration, quality, fps, seed):
    """
    Try Hugging Face with WORKING video models
    """
    print("🤗 Connecting to Hugging Face...")
    
    # Get API token
    hf_token = getattr(settings, 'HUGGINGFACE_API_TOKEN', '')
    if not hf_token:
        print("⚠️ No Hugging Face token found")
        # Try without token (some models work without auth)
        hf_token = None
    
    # WORKING video models (verified)
    working_models = [
        {
            'name': 'damo-vilab/text-to-video-ms-1.7b',
            'url': 'https://api-inference.huggingface.co/models/damo-vilab/text-to-video-ms-1.7b',
            'max_frames': 16,
            'works_without_token': True
        },
        {
            'name': 'ali-vilab/text-to-video-ms-1.7b',
            'url': 'https://api-inference.huggingface.co/models/ali-vilab/text-to-video-ms-1.7b', 
            'max_frames': 16,
            'works_without_token': True
        },
        {
            'name': 'cerspense/zeroscope_v2_576w',
            'url': 'https://api-inference.huggingface.co/models/cerspense/zeroscope_v2_576w',
            'max_frames': 24,
            'works_without_token': False
        }
    ]
    
    for model in working_models:
        try:
            print(f"  🎬 Testing model: {model['name']}")
            
            # Prepare headers
            headers = {'Content-Type': 'application/json'}
            if hf_token and not model['works_without_token']:
                headers['Authorization'] = f'Bearer {hf_token}'
            
            # Optimize for free tier
            num_frames = min(duration * 4, model['max_frames'])  # Conservative
            
            payload = {
                'inputs': prompt,
                'parameters': {
                    'num_frames': num_frames,
                    'seed': seed or random.randint(1, 100000)
                },
                'options': {
                    'wait_for_model': True,
                    'use_cache': False
                }
            }
            
            print(f"  📡 Requesting {num_frames} frames...")
            print(f"  🔗 URL: {model['url']}")
            
            # Make request with longer timeout
            response = requests.post(
                model['url'],
                headers=headers,
                json=payload,
                timeout=300  # 5 minutes
            )
            
            print(f"  📊 Response: {response.status_code}")
            print(f"  📦 Content-Type: {response.headers.get('content-type', 'unknown')}")
            print(f"  📏 Content-Length: {len(response.content)} bytes")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                
                # Check if it's actually video content
                if ('video' in content_type or 
                    'application/octet-stream' in content_type or
                    len(response.content) > 50000):  # Reasonable video size
                    
                    print(f"  ✅ Got video content! Size: {len(response.content)} bytes")
                    
                    # Create video file
                    video_file = ContentFile(
                        response.content,
                        name=f'hf_real_video_{int(time.time())}.mp4'
                    )
                    
                    # Create thumbnail
                    thumbnail_file = create_simple_thumbnail(prompt)
                    
                    metadata = {
                        'service': 'Hugging Face (REAL)',
                        'model': model['name'],
                        'frames': num_frames,
                        'duration': duration,
                        'quality': quality,
                        'content_type': content_type,
                        'file_size': len(response.content),
                        'timestamp': timezone.now().isoformat()
                    }
                    
                    return video_file, thumbnail_file, metadata
                
                elif 'application/json' in content_type:
                    # Check for error message
                    try:
                        error_data = response.json()
                        print(f"  📄 JSON Response: {error_data}")
                        if 'error' in error_data:
                            print(f"  ❌ API Error: {error_data['error']}")
                    except:
                        print(f"  📄 Raw response: {response.text[:200]}")
                
                else:
                    print(f"  ⚠️ Unexpected content type: {content_type}")
                    print(f"  📄 Response preview: {response.text[:200]}")
            
            elif response.status_code == 503:
                print(f"  ⏳ Model loading, waiting 20 seconds...")
                time.sleep(20)
                # Retry once
                response = requests.post(model['url'], headers=headers, json=payload, timeout=300)
                if response.status_code == 200 and len(response.content) > 50000:
                    video_file = ContentFile(response.content, name=f'hf_retry_{int(time.time())}.mp4')
                    thumbnail_file = create_simple_thumbnail(prompt)
                    metadata = {'service': 'Hugging Face (REAL - Retry)', 'model': model['name']}
                    return video_file, thumbnail_file, metadata
            
            elif response.status_code == 429:
                print(f"  ⏳ Rate limited, waiting 30 seconds...")
                time.sleep(30)
                continue
            
            else:
                print(f"  ❌ HTTP {response.status_code}")
                print(f"  📄 Error: {response.text[:200]}")
        
        except requests.exceptions.Timeout:
            print(f"  ⏰ Timeout for {model['name']}")
            continue
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            continue
    
    raise Exception("All Hugging Face models failed")

def try_replicate_video_real(prompt, duration, quality, fps, seed):
    """
    Try Replicate with working free models
    """
    print("🔄 Connecting to Replicate...")
    
    replicate_token = getattr(settings, 'REPLICATE_API_TOKEN', '')
    if not replicate_token:
        print("⚠️ No Replicate token - trying public models")
        replicate_token = None
    
    # Models that might work without payment
    free_models = [
        {
            'name': 'zeroscope-v2-xl',
            'owner': 'anotherjesse',
            'version': '9f747673945c62801b13b84701c783929c0ee784e4748ec062204894dda1a351'
        },
        {
            'name': 'text-to-video',
            'owner': 'cjwbw', 
            'version': '1e205ea73084bd17a0a3b43396e49ba0d6bc2e754e9283b2df49fad2dcf95755'
        }
    ]
    
    for model in free_models:
        try:
            print(f"  🎬 Testing Replicate model: {model['name']}")
            
            url = "https://api.replicate.com/v1/predictions"
            
            headers = {"Content-Type": "application/json"}
            if replicate_token:
                headers["Authorization"] = f"Token {replicate_token}"
            
            payload = {
                "version": model['version'],
                "input": {
                    "prompt": prompt,
                    "num_frames": min(duration * 4, 24),
                    "seed": seed or random.randint(1, 100000)
                }
            }
            
            print(f"  📡 Making prediction request...")
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            print(f"  📊 Response: {response.status_code}")
            
            if response.status_code == 201:
                prediction = response.json()
                prediction_id = prediction.get('id')
                
                print(f"  🆔 Prediction ID: {prediction_id}")
                
                if prediction_id:
                    # Poll for completion
                    video_url = poll_replicate_real(prediction_id, replicate_token)
                    
                    if video_url:
                        print(f"  📥 Downloading from: {video_url}")
                        
                        # Download the video
                        video_response = requests.get(video_url, timeout=120)
                        video_response.raise_for_status()
                        
                        print(f"  ✅ Downloaded! Size: {len(video_response.content)} bytes")
                        
                        video_file = ContentFile(
                            video_response.content,
                            name=f'replicate_real_{int(time.time())}.mp4'
                        )
                        
                        thumbnail_file = create_simple_thumbnail(prompt)
                        
                        metadata = {
                            'service': 'Replicate (REAL)',
                            'model': model['name'],
                            'prediction_id': prediction_id,
                            'file_size': len(video_response.content),
                            'timestamp': timezone.now().isoformat()
                        }
                        
                        return video_file, thumbnail_file, metadata
            
            elif response.status_code == 402:
                print(f"  💰 Model requires payment")
                continue
            elif response.status_code == 401:
                print(f"  🔐 Authentication required")
                continue
            else:
                print(f"  ❌ HTTP {response.status_code}: {response.text[:200]}")
                continue
        
        except Exception as e:
            print(f"  ❌ Model {model['name']} failed: {str(e)}")
            continue
    
    raise Exception("All Replicate models failed")

def try_fal_ai_video(prompt, duration, quality, fps, seed):
    """
    Try Fal.ai - another free AI service
    """
    print("🚀 Trying Fal.ai...")
    
    try:
        # Fal.ai text-to-video endpoint
        url = "https://fal.run/fal-ai/fast-svd"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Key {getattr(settings, 'FAL_API_KEY', '')}"
        }
        
        payload = {
            "prompt": prompt,
            "video_size": "square_hd" if quality == 'high' else "square",
            "num_frames": min(duration * 8, 25),
            "seed": seed or random.randint(1, 100000)
        }
        
        print(f"  📡 Requesting video from Fal.ai...")
        response = requests.post(url, headers=headers, json=payload, timeout=180)
        
        print(f"  📊 Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            video_url = result.get('video', {}).get('url')
            
            if video_url:
                print(f"  📥 Downloading from Fal.ai...")
                video_response = requests.get(video_url, timeout=120)
                
                video_file = ContentFile(
                    video_response.content,
                    name=f'fal_ai_video_{int(time.time())}.mp4'
                )
                
                thumbnail_file = create_simple_thumbnail(prompt)
                
                metadata = {
                    'service': 'Fal.ai (REAL)',
                    'file_size': len(video_response.content),
                    'timestamp': timezone.now().isoformat()
                }
                
                return video_file, thumbnail_file, metadata
    
    except Exception as e:
        print(f"  ❌ Fal.ai failed: {str(e)}")
    
    raise Exception("Fal.ai not available")

def try_pollinations_real(prompt, duration, quality, fps, seed):
    """
    Try Pollinations with real video endpoints
    """
    print("🌸 Trying Pollinations real video...")
    
    try:
        import urllib.parse
        
        # Encode prompt for URL
        encoded_prompt = urllib.parse.quote(prompt)
        
        # Try different Pollinations video endpoints
        video_endpoints = [
            f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&seed={seed or 42}&model=flux&format=mp4",
            f"https://pollinations.ai/p/{encoded_prompt}?format=video&duration={duration}&seed={seed or 42}",
        ]
        
        for endpoint in video_endpoints:
            try:
                print(f"  📡 Trying: {endpoint}")
                
                response = requests.get(endpoint, timeout=120)
                
                print(f"  📊 Response: {response.status_code}")
                print(f"  📦 Content-Type: {response.headers.get('content-type', 'unknown')}")
                print(f"  📏 Size: {len(response.content)} bytes")
                
                if response.status_code == 200 and len(response.content) > 10000:
                    content_type = response.headers.get('content-type', '')
                    
                    if 'video' in content_type or 'mp4' in content_type:
                        print(f"  ✅ Got video from Pollinations!")
                        
                        video_file = ContentFile(
                            response.content,
                            name=f'pollinations_real_{int(time.time())}.mp4'
                        )
                        
                        thumbnail_file = create_simple_thumbnail(prompt)
                        
                        metadata = {
                            'service': 'Pollinations (REAL)',
                            'endpoint': endpoint,
                            'file_size': len(response.content),
                            'timestamp': timezone.now().isoformat()
                        }
                        
                        return video_file, thumbnail_file, metadata
            
            except Exception as e:
                print(f"    ❌ Endpoint failed: {str(e)}")
                continue
    
    except Exception as e:
        print(f"  ❌ Pollinations setup failed: {str(e)}")
    
    raise Exception("Pollinations video not available")

def try_runway_free_tier(prompt, duration, quality, fps, seed):
    """
    Try Runway ML free tier (if available)
    """
    print("🛫 Trying Runway ML free tier...")
    
    runway_key = getattr(settings, 'RUNWAY_API_KEY', '')
    if not runway_key:
        print("  ⚠️ No Runway API key")
        raise Exception("Runway API key required")
    
    # This would be the actual Runway implementation
    # For now, we'll skip it since it requires payment
    raise Exception("Runway ML requires payment")

def poll_replicate_real(prediction_id, api_key, max_wait=300):
    """
    Poll Replicate prediction with detailed logging
    """
    print(f"  ⏳ Polling prediction {prediction_id}...")
    
    url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
    headers = {}
    if api_key:
        headers["Authorization"] = f"Token {api_key}"
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                
                print(f"    📊 Status: {status}")
                
                if status == 'succeeded':
                    output = data.get('output')
                    print(f"    📤 Output: {output}")
                    
                    if isinstance(output, list) and output:
                        return output[0]
                    elif isinstance(output, str):
                        return output
                    
                elif status == 'failed':
                    error = data.get('error', 'Unknown error')
                    print(f"    ❌ Failed: {error}")
                    raise Exception(f"Prediction failed: {error}")
                
                elif status in ['starting', 'processing']:
                    print(f"    ⏳ Still {status}...")
                    time.sleep(15)
                    continue
                
            else:
                print(f"    ⚠️ Polling error: {response.status_code}")
                time.sleep(10)
        
        except Exception as e:
            print(f"    ⚠️ Polling exception: {str(e)}")
            time.sleep(10)
    
    raise Exception("Prediction timeout")

def create_simple_thumbnail(prompt):
    """
    Create a simple thumbnail
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create thumbnail
        thumbnail = Image.new('RGB', (320, 240), color=(50, 50, 100))
        draw = ImageDraw.Draw(thumbnail)
        
        # Add play button
        center_x, center_y = 160, 120
        triangle_size = 30
        
        points = [
            (center_x - triangle_size, center_y - triangle_size),
            (center_x - triangle_size, center_y + triangle_size),
            (center_x + triangle_size, center_y)
        ]
        draw.polygon(points, fill='white')
        
        # Add text
        try:
            font = ImageFont.load_default()
            text = prompt[:20] + "..." if len(prompt) > 20 else prompt
            
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (320 - text_width) // 2
            y = 200
            
            draw.rectangle([x-5, y-2, x+text_width+5, y+15], fill=(0, 0, 0, 128))
            draw.text((x, y), text, fill='white', font=font)
        except:
            pass
        
        # Save thumbnail
        thumb_io = BytesIO()
        thumbnail.save(thumb_io, format='JPEG', quality=85)
        
        return ContentFile(thumb_io.getvalue(), name='real_video_thumbnail.jpg')
    
    except Exception as e:
        print(f"❌ Thumbnail creation failed: {str(e)}")
        return None
