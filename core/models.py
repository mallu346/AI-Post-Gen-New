import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from PIL import Image
import os

class CustomUser(AbstractUser):
    """Extended User model with additional fields."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    
    # Profile fields
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics/', 
        blank=True,
        null=True
    )
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize profile picture if it exists
        if self.profile_picture and hasattr(self.profile_picture, 'path'):
            try:
                img = Image.open(self.profile_picture.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.profile_picture.path)
            except Exception:
                pass

class StylePreset(models.Model):
    """Predefined styles for image generation."""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    prompt_suffix = models.TextField(help_text="Additional prompt text to append")
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class GeneratedImage(models.Model):
    """Model for AI-generated images."""
    SERVICE_CHOICES = [
        ('pollinations', 'Pollinations AI'),
        ('huggingface', 'Hugging Face'),
        ('deepai', 'DeepAI'),
        ('mock', 'Mock Generator'),
        ('replicate', 'Replicate'),
        ('unknown', 'Unknown'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='generated_images')
    prompt = models.TextField()
    style_preset = models.ForeignKey(StylePreset, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='generated_images/')
    seed = models.IntegerField(null=True, blank=True)
    width = models.IntegerField(default=512)
    height = models.IntegerField(default=512)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Service tracking fields
    generation_source = models.CharField(
        max_length=20, 
        choices=SERVICE_CHOICES, 
        default='unknown',
        help_text="Which AI service generated this image"
    )
    
    generation_metadata = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Additional metadata about the generation process"
    )
    
    # Hashtags field
    hashtags = models.TextField(
        blank=True, 
        null=True, 
        help_text="Generated hashtags for social sharing"
    )
    
    def __str__(self):
        return f"Image by {self.user.username} - {self.prompt[:50]}"
    
    class Meta:
        ordering = ['-created_at']
    
    def delete(self, *args, **kwargs):
        # Delete the image file when the model instance is deleted
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)
    
    def get_file_size_kb(self):
        """Get file size in KB"""
        if self.image and hasattr(self.image, 'path') and os.path.exists(self.image.path):
            return round(os.path.getsize(self.image.path) / 1024, 1)
        return 0
    
    def get_service_display_name(self):
        """Get human-readable service name"""
        service_names = {
            'pollinations': 'Pollinations AI',
            'huggingface': 'Hugging Face',
            'deepai': 'DeepAI',
            'mock': 'Mock Generator',
            'replicate': 'Replicate',
            'unknown': 'Unknown Service'
        }
        return service_names.get(self.generation_source, 'Unknown Service')
    
    def get_hashtags_list(self):
        """Return hashtags as a list."""
        if self.hashtags:
            return [tag.strip() for tag in self.hashtags.split(',') if tag.strip()]
        return []
    
    def set_hashtags_list(self, hashtag_list):
        """Set hashtags from a list."""
        self.hashtags = ', '.join(hashtag_list) if hashtag_list else ''

class Post(models.Model):
    """Social media posts containing generated images."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posts')
    generated_image = models.ForeignKey(GeneratedImage, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} by {self.user.username}"
    
    class Meta:
        ordering = ['-created_at']
    
    def get_tags_list(self):
        """Return tags as a list."""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def like_count(self):
        """Return the number of likes for this post."""
        return self.likes.count()
    
    def comment_count(self):
        """Return the number of comments for this post."""
        return self.comments.count()

class Like(models.Model):
    """Like model for posts."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'post')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"

class Comment(models.Model):
    """Comment model for posts."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"
    
    class Meta:
        ordering = ['created_at']

class Feedback(models.Model):
    """User feedback model."""
    RATING_CHOICES = [
        (1, '1 - Very Poor'),
        (2, '2 - Poor'),
        (3, '3 - Average'),
        (4, '4 - Good'),
        (5, '5 - Excellent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='feedback')
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback from {self.user.username} - {self.rating}/5"
    
    class Meta:
        ordering = ['-created_at']
