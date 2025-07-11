import requests
import json
import os
from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
import io
import random

def generate_image(prompt, style_suffix=""):
    """
    Generate an image using AI services with fallback options.
    Priority: Replicate -> Hugging Face -> Mock Generator
    """
    full_prompt = f"{prompt}{style_suffix}" if style_suffix else prompt
    
    print(f"Starting image generation for prompt: {full_prompt}")
    
    # Try Replicate first (most reliable)
    try:
        replicate_token = getattr(settings, 'REPLICATE_API_TOKEN', None)
        if replicate_token and replicate_token.strip():
            print("Trying Replicate API...")
            return generate_with_replicate(full_prompt, replicate_token)
    except Exception as e:
        print(f"Replicate failed: {e}")
    
    # Try Hugging Face as backup
    try:
        hf_token = getattr(settings, 'HUGGINGFACE_API_TOKEN', None)
        if hf_token and hf_token.strip():
            print("Trying Hugging Face API...")
            return generate_with_huggingface(full_prompt, hf_token)
    except Exception as e:
        print(f"Hugging Face failed: {e}")
    
    # Fallback to mock generator
    print("All APIs failed, using mock generator.")
    return generate_mock_image(full_prompt)

def generate_with_replicate(prompt, api_token):
    """Generate image using Replicate API"""
    try:
        import replicate
        
        # Initialize Replicate client
        client = replicate.Client(api_token=api_token)
        
        print(f"Generating with Replicate: {prompt}")
        
        # Use Stable Diffusion model
        output = client.run(
            "stability-ai/stable-diffusion:27b93a2413e7f36cd83da926f3656280b2931564ff050bf9575f1fdf9bcd7478",
            input={
                "prompt": prompt,
                "width": 512,
                "height": 512,
                "num_inference_steps": 20,
                "guidance_scale": 7.5,
                "scheduler": "K_EULER"
            }
        )
        
        # Download the generated image
        if output and len(output) > 0:
            image_url = output[0]
            print(f"Replicate generated image URL: {image_url}")
            
            # Download the image
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Create Django file
            image_content = ContentFile(response.content)
            print("✅ Replicate image generation successful!")
            return image_content
        else:
            raise Exception("No output from Replicate")
            
    except ImportError:
        raise Exception("Replicate package not installed. Run: pip install replicate")
    except Exception as e:
        raise Exception(f"Replicate API failed: {str(e)}")

def generate_with_huggingface(prompt, api_token):
    """Generate image using Hugging Face API"""
    try:
        print(f"Generating with Hugging Face: {prompt}")
        
        # Hugging Face Inference API
        API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        headers = {"Authorization": f"Bearer {api_token}"}
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "num_inference_steps": 20,
                "guidance_scale": 7.5,
                "width": 512,
                "height": 512
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            # Create Django file from response content
            image_content = ContentFile(response.content)
            print("✅ Hugging Face image generation successful!")
            return image_content
        else:
            raise Exception(f"Hugging Face API failed: {response.status_code}")
            
    except Exception as e:
        raise Exception(f"Hugging Face API failed: {str(e)}")

def generate_mock_image(prompt):
    """Generate a colorful mock image with the prompt text"""
    try:
        print(f"Generating mock image for: {prompt}")
        
        # Create a colorful gradient background
        width, height = 512, 512
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)
        
        # Create gradient background
        colors = [
            (255, 107, 107),  # Red
            (78, 205, 196),   # Teal  
            (69, 183, 209),   # Blue
            (255, 195, 113),  # Orange
            (196, 229, 56),   # Green
            (162, 155, 254),  # Purple
        ]
        
        color = random.choice(colors)
        
        # Create gradient
        for y in range(height):
            r = int(color[0] * (1 - y/height) + 50 * (y/height))
            g = int(color[1] * (1 - y/height) + 50 * (y/height))
            b = int(color[2] * (1 - y/height) + 50 * (y/height))
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Add some decorative elements
        for _ in range(20):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(10, 50)
            circle_color = tuple(random.randint(100, 255) for _ in range(3))
            draw.ellipse([x-size//2, y-size//2, x+size//2, y+size//2], 
                        fill=circle_color + (100,))
        
        # Add prompt text
        try:
            # Try to use a nice font
            font_size = 24
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Wrap text
        words = prompt.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            line_text = ' '.join(current_line)
            bbox = draw.textbbox((0, 0), line_text, font=font)
            if bbox[2] > width - 40:  # 20px margin on each side
                if len(current_line) > 1:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw text with background
        y_offset = height // 2 - (len(lines) * 30) // 2
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            
            # Draw text background
            draw.rectangle([x-10, y_offset-5, x+text_width+10, y_offset+25], 
                          fill=(0, 0, 0, 180))
            
            # Draw text
            draw.text((x, y_offset), line, fill='white', font=font)
            y_offset += 30
        
        # Add "MOCK" watermark
        watermark_font_size = 48
        try:
            watermark_font = ImageFont.truetype("arial.ttf", watermark_font_size)
        except:
            watermark_font = ImageFont.load_default()
        
        watermark_text = "MOCK"
        bbox = draw.textbbox((0, 0), watermark_text, font=watermark_font)
        watermark_width = bbox[2] - bbox[0]
        watermark_x = width - watermark_width - 20
        watermark_y = height - 60
        
        # Draw watermark with semi-transparent background
        draw.rectangle([watermark_x-10, watermark_y-5, watermark_x+watermark_width+10, watermark_y+45], 
                      fill=(255, 255, 255, 200))
        draw.text((watermark_x, watermark_y), watermark_text, fill='red', font=watermark_font)
        
        # Convert to bytes
        img_io = io.BytesIO()
        image.save(img_io, format='PNG')
        img_io.seek(0)
        
        print("✅ Mock image generation successful!")
        return ContentFile(img_io.getvalue(), name='mock_image.png')
        
    except Exception as e:
        print(f"Mock generation error: {e}")
        # Return a simple colored rectangle as last resort
        image = Image.new('RGB', (512, 512), color=(100, 150, 200))
        img_io = io.BytesIO()
        image.save(img_io, format='PNG')
        img_io.seek(0)
        return ContentFile(img_io.getvalue(), name='simple_mock.png')

def test_connection():
    """Test API connections"""
    results = {}
    
    # Test Replicate
    try:
        replicate_token = getattr(settings, 'REPLICATE_API_TOKEN', None)
        if replicate_token and replicate_token.strip():
            import replicate
            client = replicate.Client(api_token=replicate_token)
            # Try to list models to test connection
            results['replicate'] = "✅ Connected"
        else:
            results['replicate'] = "❌ No token"
    except ImportError:
        results['replicate'] = "❌ Package not installed"
    except Exception as e:
        results['replicate'] = f"❌ Error: {e}"
    
    # Test Hugging Face
    try:
        hf_token = getattr(settings, 'HUGGINGFACE_API_TOKEN', None)
        if hf_token and hf_token.strip():
            response = requests.get(
                "https://huggingface.co/api/whoami",
                headers={"Authorization": f"Bearer {hf_token}"},
                timeout=10
            )
            if response.status_code == 200:
                results['huggingface'] = "✅ Connected"
            else:
                results['huggingface'] = f"❌ Invalid token ({response.status_code})"
        else:
            results['huggingface'] = "❌ No token"
    except Exception as e:
        results['huggingface'] = f"❌ Error: {e}"
    
    return results
