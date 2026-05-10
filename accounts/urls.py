from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

app_name = "accounts"
urlpatterns = [
    path('signup/', views.UserRegistrationView.as_view(), name='user-register'),
    path('login/', views.UserLoginView.as_view(), name='user-login'),
    path('logout/', views.UserLogoutView.as_view(), name='user-logout'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('profile/edit/', views.UserProfileEditView.as_view(), name='edit-profile'),
    path('profile/delete/', views.UserDeleteView.as_view(), name='user-delete'),
    path('profile/edit/password/', 
         auth_views.PasswordChangeView.as_view(
             template_name="accounts/password_change.html",
             success_url=reverse_lazy('accounts:password_change_done')
         ), 
         name='password_change'),
    path('profile/edit/password/done/', 
         auth_views.PasswordChangeDoneView.as_view(
             template_name="accounts/password_change_done.html"
         ), 
         name='password_change_done'),
]