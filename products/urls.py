from django.urls import path
from . import views


app_name = 'products'
urlpatterns = [
    path('all/', views.ProductListView.as_view(), name="all-products"),
    path('confirm/<str:name>', views.BuyConfirmationView.as_view(), name="buy-confirm"),
]