from django.urls import path, include
from . import views


app_name = 'products'
urlpatterns = [
    path('all/', views.ProductListView.as_view(), name="all-products"),
    path('confirm/<slug:product_slug>/', views.BuyConfirmationView.as_view(), name="buy-confirm"),
    path('during-process/', views.DuringProcessView.as_view(), name="during-process"),
    path('completed-process/', views.CompletedProcessView.as_view(), name="completed-process"),
    path("like-unlike/<int:product_pk>/", views.MakeFavoriteView.as_view(), name="product-like"),
    path("favorites/", views.UserFavoritesListView.as_view(), name="user-favorites"),
    # API urls
    path('api/v1/product/all/', views.AllProductsAPIView.as_view(), name='api-all-products'),
    path('api/v1/product/<slug:product_slug>/', views.ProductRetrieveAPIView.as_view(), name='api-product-retrieve'),
]
