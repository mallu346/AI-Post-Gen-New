from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import CustomUser, GeneratedImage, Post, Comment, Feedback, StylePreset

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class ImageGenerationForm(forms.Form):
    DIMENSION_CHOICES = [
        (512, '512x512 (Square)'),
        (768, '768x768 (Large Square)'),
        (512, '512x768 (Portrait)'),
        (768, '768x512 (Landscape)'),
    ]
    
    prompt = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Describe the image you want to generate...',
            'class': 'form-control'
        })
    )
    
    style_preset = forms.ModelChoiceField(
        queryset=StylePreset.objects.filter(is_active=True),
        required=False,
        empty_label="No style preset",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    width = forms.ChoiceField(
        choices=[(512, '512'), (768, '768')],
        initial=512,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    height = forms.ChoiceField(
        choices=[(512, '512'), (768, '768')],
        initial=512,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    seed = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=1000000,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Optional: Enter a seed for reproducible results',
            'class': 'form-control'
        })
    )
    
    def clean_prompt(self):
        prompt = self.cleaned_data.get('prompt')
        if len(prompt.strip()) < 3:
            raise ValidationError("Prompt must be at least 3 characters long.")
        return prompt.strip()

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Give your creation a title...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your artwork...'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Add tags separated by commas (e.g., digital art, fantasy, portrait)'
            })
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title.strip()) < 3:
            raise ValidationError("Title must be at least 3 characters long.")
        return title.strip()

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write a comment...'
            })
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your thoughts about the platform...'
            })
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'bio', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'})
        }
