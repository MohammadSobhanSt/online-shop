from django.contrib import messages
from django.shortcuts import redirect, render
from .models import CustomUser
from django.views import View
from .forms import UserRegistrationForm
from django.contrib.auth import login, logout


class UserRegistrationView(View):
    template_name = 'accounts/register.html'
    form_class = UserRegistrationForm

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {"form":form})
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = form.save(commit=False)
            password = cd['password']
            user.set_password(password)
            user.save()
            
            if user is not None:
                login(request, user)
                msg = 'Your account created successfully 🎉. Thank you for choosing us :)'
                messages.success(request, msg, 'success')
                return redirect('home:home')
            
        return render(request, self.template_name, {"form":form})
        
        
