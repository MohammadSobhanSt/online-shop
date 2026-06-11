from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from .forms import BuyConfirmationForm
from .models import Product, Purchase
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


class ProductListView(View):
    template_name = 'products/product_list.html'
    
    def get(self, request):
        products = Product.objects.all().order_by("-product_count")
        return render(request, self.template_name, {'products':products})


class BuyConfirmationView(LoginRequiredMixin, View):
    template_name = "products/buy_confirmation.html"
    form_class = BuyConfirmationForm
    
    def dispatch(self, request, *args, **kwargs):
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