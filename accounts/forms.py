from django import forms
from django.core.exceptions import ValidationError
from .models import CustomUser


class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password']
        
        widgets = {
                    'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
                    'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
                    'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}),
                }
                
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email already exists...")
        
        return email
        
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("This username already taken please try another one...")
        
        return username
        
        
class UserLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}
    ))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}
    ))