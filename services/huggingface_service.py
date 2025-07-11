import requests
import io
import base64
from PIL import Image
from django.conf import settings
from django.core.files.base import ContentFile
import time
import random

class HuggingFaceService:
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        self.headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_TOKEN}"}
        self.max_retries = 3
        self.retry_delay = 2
    
    def generate_image(self, prompt, style_preset=None, width=512, height=512, seed=None):
        """
        Generate an image using Stable Diffusion via Hugging Face API
        """
        # Enhance prompt with style preset
        enhanced_prompt = prompt
        if style_preset and style_preset.prompt_suffix:
            enhanced_prompt = f"{prompt}, {style_preset.prompt_suffix}"
        
        payload = {
            "inputs": enhanced_prompt,
            "parameters": {
                "width": width,
                "height": height,
                "num_inference_steps": 20,
                "guidance_scale": 7.5,
            }
        }
        
        if seed:
            payload["parameters"]["seed"] = seed
        else:
            payload["parameters"]["seed"] = random.randint(1, 1000000)
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=60
                )
                
                if response.status_code == 200:
                    # Convert response to image
                    image_bytes = response.content
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    # Convert to RGB if necessary
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    # Save to BytesIO
                    img_io = io.BytesIO()
                    image.save(img_io, format='JPEG', quality=95)
                    img_io.seek(0)
                    
                    return {
                        'success': True,
                        'image_data': img_io,
                        'seed': payload["parameters"]["seed"],
                        'enhanced_prompt': enhanced_prompt
                    }
                
                elif response.status_code == 503:
                    # Model is loading, wait and retry
                    error_data = response.json()
                    estimated_time = error_data.get('estimated_time', 20)
                    time.sleep(min(estimated_time, 30))
                    continue
                
                else:
                    return {
                        'success': False,
                        'error': f"API Error: {response.status_code} - {response.text}"
                    }
            
            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                return {
                    'success': False,
                    'error': "Request timeout. Please try again."
                }
            
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Unexpected error: {str(e)}"
                }
        
        return {
            'success': False,
            'error': "Failed to generate image after multiple attempts."
        }
    
    def get_model_status(self):
        """
        Check if the model is available
        """
        try:
            response = requests.get(
                f"{self.api_url}/status",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
