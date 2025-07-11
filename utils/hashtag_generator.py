import re
import random
from typing import List, Optional

class HashtagGenerator:
    """Generate relevant hashtags for AI-generated images"""
    
    # Base hashtags that are always relevant
    BASE_HASHTAGS = [
        'aiart', 'artificialintelligence', 'digitalart', 'generativeart',
        'machinelearning', 'aiartist', 'computervision', 'deeplearning'
    ]
    
    # Style-based hashtags
    STYLE_HASHTAGS = {
        'photorealistic': ['photorealistic', 'hyperrealistic', 'realistic', 'photography'],
        'anime': ['anime', 'manga', 'animeart', 'otaku', 'kawaii'],
        'abstract': ['abstract', 'abstractart', 'modernart', 'contemporary'],
        'fantasy': ['fantasy', 'fantasyart', 'magical', 'mythical', 'enchanted'],
        'cyberpunk': ['cyberpunk', 'futuristic', 'neon', 'scifi', 'dystopian'],
        'vintage': ['vintage', 'retro', 'classic', 'oldschool', 'nostalgic'],
        'minimalist': ['minimalist', 'clean', 'simple', 'geometric'],
        'surreal': ['surreal', 'dreamlike', 'psychedelic', 'trippy'],
        'portrait': ['portrait', 'face', 'character', 'person'],
        'landscape': ['landscape', 'nature', 'scenery', 'outdoor']
    }
    
    # Content-based hashtags
    CONTENT_HASHTAGS = {
        # Animals
        'cat': ['cat', 'feline', 'kitten', 'pet'],
        'dog': ['dog', 'canine', 'puppy', 'pet'],
        'bird': ['bird', 'flying', 'wings', 'nature'],
        'dragon': ['dragon', 'mythical', 'fantasy', 'legendary'],
        
        # Nature
        'forest': ['forest', 'trees', 'nature', 'green', 'woodland'],
        'ocean': ['ocean', 'sea', 'water', 'blue', 'waves'],
        'mountain': ['mountain', 'peak', 'landscape', 'nature'],
        'flower': ['flower', 'floral', 'bloom', 'garden', 'nature'],
        'sunset': ['sunset', 'golden', 'warm', 'evening', 'sky'],
        'space': ['space', 'galaxy', 'stars', 'cosmic', 'universe'],
        
        # Colors
        'red': ['red', 'crimson', 'scarlet', 'warm'],
        'blue': ['blue', 'azure', 'cool', 'calm'],
        'green': ['green', 'emerald', 'nature', 'fresh'],
        'purple': ['purple', 'violet', 'mystical', 'royal'],
        'gold': ['gold', 'golden', 'luxury', 'precious'],
        
        # Moods
        'dark': ['dark', 'mysterious', 'gothic', 'shadow'],
        'bright': ['bright', 'vibrant', 'colorful', 'cheerful'],
        'peaceful': ['peaceful', 'calm', 'serene', 'tranquil'],
        'dramatic': ['dramatic', 'intense', 'powerful', 'bold']
    }
    
    # Trending hashtags (can be updated periodically)
    TRENDING_HASHTAGS = [
        'midjourney', 'stablediffusion', 'dalle', 'aiartcommunity',
        'promptengineering', 'neuralnetwork', 'creativity', 'innovation',
        'digitalcreator', 'artoftheday', 'airevolution', 'futureofart'
    ]
    
    @classmethod
    def generate_hashtags(cls, prompt: str, style_preset: Optional[str] = None, max_hashtags: int = 15) -> List[str]:
        """
        Generate relevant hashtags based on prompt and style
        
        Args:
            prompt: The user's prompt text
            style_preset: The selected style preset name
            max_hashtags: Maximum number of hashtags to return
            
        Returns:
            List of hashtag strings (without # symbol)
        """
        hashtags = set()
        prompt_lower = prompt.lower()
        
        # Add base AI art hashtags
        hashtags.update(random.sample(cls.BASE_HASHTAGS, min(3, len(cls.BASE_HASHTAGS))))
        
        # Add style-based hashtags
        if style_preset:
            style_lower = style_preset.lower()
            for style_key, style_tags in cls.STYLE_HASHTAGS.items():
                if style_key in style_lower:
                    hashtags.update(random.sample(style_tags, min(2, len(style_tags))))
                    break
        
        # Add content-based hashtags
        for content_key, content_tags in cls.CONTENT_HASHTAGS.items():
            if content_key in prompt_lower:
                hashtags.update(random.sample(content_tags, min(2, len(content_tags))))
        
        # Add some trending hashtags
        hashtags.update(random.sample(cls.TRENDING_HASHTAGS, min(3, len(cls.TRENDING_HASHTAGS))))
        
        # Extract keywords from prompt
        prompt_keywords = cls._extract_keywords_from_prompt(prompt)
        hashtags.update(prompt_keywords[:3])  # Add up to 3 keywords from prompt
        
        # Convert to list and limit
        hashtag_list = list(hashtags)[:max_hashtags]
        
        # Clean hashtags (remove special characters, ensure valid format)
        cleaned_hashtags = []
        for tag in hashtag_list:
            cleaned_tag = cls._clean_hashtag(tag)
            if cleaned_tag and len(cleaned_tag) > 2:  # Only add valid hashtags
                cleaned_hashtags.append(cleaned_tag)
        
        return cleaned_hashtags[:max_hashtags]
    
    @classmethod
    def _extract_keywords_from_prompt(cls, prompt: str) -> List[str]:
        """Extract potential hashtag keywords from the prompt"""
        # Remove common words and extract meaningful terms
        common_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
            'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
        }
        
        # Extract words, clean them, and filter
        words = re.findall(r'\b[a-zA-Z]+\b', prompt.lower())
        keywords = []
        
        for word in words:
            if (len(word) > 3 and 
                word not in common_words and 
                word.isalpha()):
                keywords.append(word)
        
        return keywords[:5]  # Return up to 5 keywords
    
    @classmethod
    def _clean_hashtag(cls, hashtag: str) -> str:
        """Clean and validate hashtag format"""
        # Remove special characters and spaces
        cleaned = re.sub(r'[^a-zA-Z0-9]', '', hashtag.lower())
        
        # Ensure it starts with a letter
        if cleaned and cleaned[0].isalpha():
            return cleaned
        
        return ''
    
    @classmethod
    def get_trending_hashtags(cls) -> List[str]:
        """Get a sample of trending hashtags for display"""
        return random.sample(cls.TRENDING_HASHTAGS, min(8, len(cls.TRENDING_HASHTAGS)))
    
    @classmethod
    def get_popular_hashtags_by_category(cls) -> dict:
        """Get popular hashtags organized by category"""
        return {
            'AI & Tech': cls.BASE_HASHTAGS[:6],
            'Styles': ['photorealistic', 'anime', 'abstract', 'fantasy', 'cyberpunk'],
            'Nature': ['landscape', 'ocean', 'forest', 'sunset', 'space'],
            'Trending': cls.TRENDING_HASHTAGS[:6]
        }
