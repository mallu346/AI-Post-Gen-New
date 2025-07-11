from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import CustomUser, Post, GeneratedImage, Comment, StylePreset

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form."""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes for styling
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
        # Update placeholders
        self.fields['username'].widget.attrs['placeholder'] = 'Choose a username'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter your email'
        self.fields['first_name'].widget.attrs['placeholder'] = 'First name (optional)'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last name (optional)'
        self.fields['password1'].widget.attrs['placeholder'] = 'Create a password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm your password'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile."""
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'bio', 'profile_picture', 'website', 'location', 'birth_date']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email address'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://your-website.com'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, Country'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

class ImageGenerationForm(forms.Form):
    """Form for AI image generation."""
    prompt = forms.CharField(
        max_length=1000,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Describe the image you want to generate...',
            'required': True
        })
    )
    style_preset = forms.ModelChoiceField(
        queryset=StylePreset.objects.filter(is_active=True),
        required=False,
        empty_label="Choose a style (optional)",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    width = forms.ChoiceField(
        choices=[
            (512, '512px'),
            (768, '768px'),
            (1024, '1024px'),
        ],
        initial=512,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    height = forms.ChoiceField(
        choices=[
            (512, '512px'),
            (768, '768px'),
            (1024, '1024px'),
        ],
        initial=512,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    seed = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Random seed (optional)'
        })
    )

class CommentForm(forms.ModelForm):
    """Form for adding comments to posts."""
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write a comment...',
                'required': True
            })
        }

class PostForm(forms.ModelForm):
    """Form for creating posts."""
    class Meta:
        model = Post
        fields = ['title', 'description', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Give your creation a title...',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your creation...'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Add tags separated by commas (e.g., art, fantasy, portrait)'
            }),
        }
