from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .forms import BuyConfirmationForm
from .models import Product, Purchase, Favorite
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .permissions import IsSeller
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from .serializer import ProductSerializer, ProductCreateSerializer, CreateUserTokenSerializer


class ProductListView(View):
    template_name = 'products/product_list.html'
    
    def get(self, request):
        user = request.user
        products = Product.objects.all().order_by("-product_count")
        user_liked_product_ids = set()
        if user.is_authenticated:
            user_liked_product_ids = set(user.favorites.values_list('product__pk', flat=True))
        return render(request, self.template_name, {'products':products, "user_liked_product_ids":user_liked_product_ids})


class BuyConfirmationView(LoginRequiredMixin, View):
    template_name = "products/buy_confirmation.html"
    form_class = BuyConfirmationForm
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        if not getattr(request.user, 'email_confirmed', False):
            messages.warning(request, "You should confirm your email first :).", "warning")
            return redirect("accounts:email-confirm")

        product = get_object_or_404(Product, slug=kwargs['product_slug'])
        if product.product_count == 0:
            messages.info(request, "Product is no more available...", "info")
            return redirect('products:all-products')

        return super().dispatch(request, *args, **kwargs)
    
        
    def get(self, request, product_slug):
        form = self.form_class()
        product = get_object_or_404(Product, slug=product_slug)        
        return render(request, self.template_name, {"form": form, "product": product})
        
    def post(self, request, product_slug):
        form = self.form_class(request.POST)
        product = get_object_or_404(Product, slug=product_slug)
        
        if form.is_valid():
            cd = form.cleaned_data
            quantity_user_want = cd['quantity_user_want']
            
            if not product.is_in_stock(quantity_user_want):
                messages.error(request, f"Only {product.product_count} items available", "danger")
                return render(request, self.template_name, {'form': form, 'product': product})
            
            try:
                total_amount = product.price * quantity_user_want
                
                Purchase.objects.create(
                    buyer=request.user,
                    product=product,
                    quantity_user_want=quantity_user_want,
                    total_amount=total_amount,
                    during_process=True
                )

                product.reduce_stock(quantity_user_want)

                msg = 'Congrats. You bought this product. You can see your order tracking from your profile.'
                messages.success(request, msg, 'success')
                return redirect('accounts:user-profile')

            except ValidationError as e:
                messages.error(request, str(e), "danger")
                return render(request, self.template_name, {'form': form, 'product': product})

        messages.error(request, "There was an error during process.", "danger")
        return render(request, self.template_name, {'form': form, 'product': product})


class DuringProcessView(LoginRequiredMixin, View):
    template_name = "products/during_process.html"

    def get(self, request):
        items = Purchase.objects.filter(buyer=request.user, during_process=True).order_by('-bought_at')
        return render(request, self.template_name, {"items":items})


class CompletedProcessView(LoginRequiredMixin, View):
    template_name = "products/completed_process.html"

    def get(self, request):
        items = Purchase.objects.filter(buyer=request.user, during_process=False).order_by('-bought_at')
        return render(request, self.template_name, {"items":items})


class UserFavoritesListView(LoginRequiredMixin, View):
    template_name = "products/user_favorites.html"

    def get(self, request):
        user = request.user
        user_liked_product_ids = set()
        if user.is_authenticated:
            user_liked_product_ids = set(user.favorites.values_list('product__pk', flat=True))
        items = Favorite.objects.filter(user=request.user)
        return render(request, self.template_name, {"items":items, "user_liked_product_ids":user_liked_product_ids})


class MakeFavoriteView(LoginRequiredMixin, View):
    template_name = "products/product_list.html"

    def post(self, request, product_pk):
        item = get_object_or_404(Product, pk=product_pk)
        like = Favorite.objects.filter(user=request.user, product=item)

        if like.exists():
            like.delete()
            messages.error(request, f"You unliked \"{item.name}\".", "danger")
        else:
            like = Favorite.objects.create(user=request.user, product=item)
            like.is_liked = True
            messages.success(request, f"You liked \"{item.name}\". You can see your favorites from your your profile.")

        referer = request.META.get('HTTP_REFERER', '')

        if '/products/favorites/' in referer:
            return redirect('products:user-favorites')
        else:
            return redirect("products:all-products")


# API views
class AllProductsAPIView(generics.ListAPIView):
    queryset = Product.objects.all().order_by("-product_count")
    serializer_class = ProductSerializer


class ProductRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'product_slug'

    def get_object(self):
        product_slug = self.kwargs.get('product_slug')
        return get_object_or_404(Product, slug=product_slug)


class ProductAddView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsSeller]
    serializer_class = ProductCreateSerializer


class UserAPILoginView(APIView):
    serializer_class = CreateUserTokenSerializer

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Both email and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, email=email, password=password)

        if user is not None and user.groups.filter(name="Seller").exists():
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "email": user.email,
            }, status=status.HTTP_200_OK)

        return Response({
            "error": "Invalid credentials or permissions."},
            status=status.HTTP_401_UNAUTHORIZED
        )