from django.contrib import messages
from django.shortcuts import redirect, render
from .models import CustomUser
from django.views import View
from .forms import UserRegistrationForm, UserLoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin


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
        

class UserLoginView(View):
    template_name = 'accounts/login.html'
    form_class = UserLoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.warning(request, "You can't login again... :)", "warning")
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {"form":form})
        
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():            
            cd = form.cleaned_data

            user = authenticate(request, email=cd['email'], password=cd['password'])
            
            if user is not None:
                login(request, user)
                messages.success(request, f'You logged in successfully. Welcome back dear {user.username} :).')
                return redirect('home:home')
            
            messages.warning(request, "Your email or password is wrong.", 'warning')
                
        return render(request, self.template_name, {"form":form})
        
        
class UserLogoutView(LoginRequiredMixin, View):
    def get(self , request):
        logout(request)
        messages.success(request, "You logged out successfully. We hope you come back soon :).")
        return redirect('home:home')