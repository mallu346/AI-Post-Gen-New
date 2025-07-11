from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
import io
import random
import uuid

def generate_mock_image(prompt, style_preset=None, width=512, height=512, seed=None):
    """
    Generate a mock image with the prompt text for testing purposes
    """
    try:
        # Set random seed if provided
        if seed:
            random.seed(seed)
        
        # Create a new image with random background color
        colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
            '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
        ]
        bg_color = random.choice(colors)
        
        # Create image
        image = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(image)
        
        # Add some geometric shapes for visual interest
        for _ in range(random.randint(3, 8)):
            shape_type = random.choice(['rectangle', 'ellipse'])
            x1 = random.randint(0, width//2)
            y1 = random.randint(0, height//2)
            x2 = random.randint(width//2, width)
            y2 = random.randint(height//2, height)
            
            shape_color = random.choice(colors)
            if shape_type == 'rectangle':
                draw.rectangle([x1, y1, x2, y2], fill=shape_color, outline='white', width=2)
            else:
                draw.ellipse([x1, y1, x2, y2], fill=shape_color, outline='white', width=2)
        
        # Add prompt text
        try:
            # Try to use a default font, fall back to basic if not available
            font_size = max(16, min(width, height) // 20)
            font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # Wrap text to fit image
        words = prompt.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] < width - 40:  # 20px margin on each side
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw text
        total_text_height = len(lines) * (font_size + 5)
        start_y = (height - total_text_height) // 2
        
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = start_y + i * (font_size + 5)
            
            # Draw text with outline for better visibility
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), line, font=font, fill='black')
            draw.text((x, y), line, font=font, fill='white')
        
        # Add style preset indicator
        if style_preset:
            style_text = f"Style: {style_preset.name}"
            bbox = draw.textbbox((0, 0), style_text, font=font)
            draw.text((10, height - 30), style_text, font=font, fill='white')
        
        # Add "MOCK" watermark
        mock_font = font
        draw.text((width - 80, 10), "MOCK", font=mock_font, fill='rgba(255,255,255,128)')
        
        # Convert to file
        image_io = io.BytesIO()
        image.save(image_io, format='PNG')
        image_io.seek(0)
        
        # Create unique filename
        filename = f"mock_{uuid.uuid4().hex[:8]}.png"
        content_file = ContentFile(image_io.getvalue(), name=filename)
        
        return image, content_file
        
    except Exception as e:
        print(f"Error generating mock image: {str(e)}")
        return None, None
