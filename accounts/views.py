from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from .models import CustomUser, Confirm
from .utilities import send_otp_email
from django.views import View
from .forms import UserRegistrationForm, UserLoginForm, UserProfileEditForm, EmailConfirmationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_views


class UserRegistrationView(View):
    template_name = 'accounts/register.html'
    form_class = UserRegistrationForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form":form})
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = form.save(commit=False)
            password = cd['password']
            user.set_password(password)
            user.email_confirmed = False
            user.save()
            
            if user is not None:
                login(request, user)
                send_otp_email(request)
                congrats_msg = 'Your account created successfully 🎉. Thank you for choosing us :)'
                messages.success(request, congrats_msg, 'success')
                return redirect('accounts:email-confirm')
            
        return render(request, self.template_name, {"form":form})


class EmailConfirmationView(LoginRequiredMixin, View):
    template_name = "accounts/email_confirm.html"
    form_class = EmailConfirmationForm

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if getattr(user, 'email_confirmed', False):
                return redirect("accounts:user-profile")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
         form = self.form_class()
         return render(request, self.template_name, {"form":form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user_input = cd["otp"]
            if hasattr(request.user, 'confirmation'):
                if request.user.confirmation.is_expired():
                    request.user.confirmation.delete()

                if user_input == request.user.confirmation.otp:
                    request.user.email_confirmed = True
                    request.user.save()
                    request.user.confirmation.delete()
                    messages.success(request, "Your account confirmed successfully.")
                    return redirect("products:all-products")
                elif user_input != request.user.confirmation.otp:
                    messages.error(request, "Your OTP code is wrong try again.", "danger")
                    return render(request, self.template_name, {"form":form})
                else:
                    messages.error(request,"There was an unknown error during the process...", "danger")
            else:
                messages.error(request, "No confirmation request found. Please request a new OTP.", "danger")
        return render(request, self.template_name, {"form":form})


class ResendConfirmationView(LoginRequiredMixin, View):
    template_name = "accounts/email_confirm.html"

    def post(self, request):
        otp_code = get_object_or_404(Confirm, user=request.user, otp=request.user.confirmation.otp)
        otp_code.delete()
        send_otp_email(request)
        return redirect("accounts:email-confirm")

class UserLoginView(View):
    template_name = 'accounts/login.html'
    form_class = UserLoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not getattr(request.user, 'email_confirmed', False):
                messages.error(request, "You must confirm your email first.", "danger")
                return redirect("accounts:email-confirm")
            messages.warning(request, "You are already logged in.", "warning")
            return redirect('home:home')

        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form":form})
        
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():            
            cd = form.cleaned_data

            user = authenticate(request, email=cd['email'], password=cd['password'])
            
            if user is not None:
                login(request, user)
                messages.success(request, f'You logged in successfully. Welcome back dear {request.user.username} :).')
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
        if not user.is_active:
            msg = "Your account is not active yet. For use all of our services you should active your account."
            messages.warning(request, msg, "warning")
        return render(request, self.template_name, {"user":user})
        
        
class UserProfileEditView(LoginRequiredMixin, View):
    form_class = UserProfileEditForm
    template_name = "accounts/profile_edit.html"

    def get(self, request):
        user = get_object_or_404(CustomUser, username=request.user.username, email=request.user.email)
        form = self.form_class(instance=user)
        return render(request, self.template_name, {"form":form})

    def post(self, request):
        old_email = request.user.email
        form = self.form_class(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            if user.email != old_email:
                user.email_confirmed = False
                user.save(update_fields=["email_confirmed"])
                send_otp_email(request)
                messages.warning(request, "To use our services please confirm your email.", "warning")
                return redirect("accounts:email-confirm")
            messages.info(request, "Your profile updated successfully.", "info")
            return redirect("accounts:user-profile")
        return render(request, self.template_name, {"form":form})


class UserPasswordResetView(auth_views.PasswordResetView):
    template_name = "accounts/password_reset_form.html"
    success_url = reverse_lazy("accounts:password_reset_done")
    email_template_name = "accounts/password_reset_email.html"


class UserPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")


class UserPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"


class UserDeleteView(LoginRequiredMixin, View):
    template_name = 'accounts/user_confirm_delete.html'
    
    def get(self, request):
        return render(request, self.template_name)
        
    def post(self, request):
        user = request.user
        user.delete()
        messages.info(request, "Your account has been deleted successfully.", 'info')
        return redirect("home:home")