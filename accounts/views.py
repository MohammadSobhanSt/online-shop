from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from .models import CustomUser
from django.views import View
from .forms import UserRegistrationForm, UserLoginForm, UserProfileEditForm
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
        
        
        
class UserProfileView(LoginRequiredMixin, View):
    template_name = 'accounts/profile.html'
    
    def get(self, request):
        user = get_object_or_404(CustomUser, username=request.user.username, email=request.user.email)
        return render(request, self.template_name, {"user":user})
        
        
class UserProfileEditView(LoginRequiredMixin, View):
    form_class = UserProfileEditForm
    template_name = "accounts/profile_edit.html"

    def get(self, request):
        user = get_object_or_404(CustomUser, username=request.user.username, email=request.user.email)
        form = self.form_class(instance=user)
        return render(request, self.template_name, {"form":form})
        
    def post(self, request):
        user = get_object_or_404(CustomUser, username=request.user.username, email=request.user.email)
        form = self.form_class(request.POST, instance=user)
        if form.is_valid():
            user.save()
            messages.info(request, "Your profile updated successfully.", "info")
            return redirect("accounts:user-profile")
        return render(request, self.template_name, {"form":form})


class UserDeleteView(LoginRequiredMixin, View):
    template_name = 'accounts/user_confirm_delete.html'
    
    def get(self, request):
        return render(request, self.template_name)
        
    def post(self, request):
        user = request.user
        user.delete()
        messages.info(request, "Your account has been deleted successfully.", 'info')
        return redirect("home:home")
