from django.urls import path
from . import views


app_name = "accounts"
urlpatterns = [
    path('signup/', views.UserRegistrationView.as_view(), name='user-register'),
    path('login/', views.UserLoginView.as_view(), name='user-login'),
    path('logout/', views.UserLogoutView.as_view(), name='user-logout'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('profile/edit/', views.UserProfileEditView.as_view(), name='edit-profile'),
    path('profile/delete/', views.UserDeleteView.as_view(), name='user-delete'),
]