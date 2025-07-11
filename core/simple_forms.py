from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """Simple user registration form."""
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class ImageGenerationForm(forms.Form):
    """Simple image generation form."""
    prompt = forms.CharField(
        max_length=1000,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Describe the image you want to generate...'
        })
    )
    width = forms.ChoiceField(
        choices=[(512, '512px'), (768, '768px'), (1024, '1024px')],
        initial=512
    )
    height = forms.ChoiceField(
        choices=[(512, '512px'), (768, '768px'), (1024, '1024px')],
        initial=512
    )
