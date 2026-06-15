from django import forms
from .models import Purchase


class BuyConfirmationForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['quantity_user_want']
        
        widgets = {
            "quantity_user_want": forms.TextInput(attrs={'class':'form-control', 'placeholder':'Enter a value'})
        }
        
        labels = {
            "quantity_user_want": "How many do you want"
        }