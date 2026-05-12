from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from .forms import BuyConfirmationForm
from .models import Product
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


class ProductListView(View):
    template_name = 'products/product_list.html'
    
    def get(self, request):
        products = Product.objects.all()
        return render(request, self.template_name, {'products':products})
        

class BuyConfirmationView(LoginRequiredMixin, View):
    template_name = "products/buy_confirmation.html"
    form_class = BuyConfirmationForm
    
    def get(self, request, name):
        form = self.form_class
        product = get_object_or_404(Product, name=name)
        return render(request, self.template_name, {"form":form, "product":product})
        
    def post(self, request, name):
        form = self.form_class(request.POST)
        product = get_object_or_404(Product, name=name)

        if form.is_valid():
            cd = form.cleaned_data
            
            product.buyer.add(request.user)
            product.quantity_user_want = cd['quantity_user_want']
            try:
                product.reduce_stock()
            except ValidationError as e:
                messages.error(request, str(e), "danger")
                return render(request, self.template_name, {'form': form, 'product': product})
                
            product.save()
            msg = 'Congrats. You bought this product. You can see your order tracking from your profile.'
            messages.success(request, msg, 'success')
            return redirect('accounts:user-profile')
            
        messages.error(request, "There was an error during proccess.", "danger")
        return render(request, self.template_name, {'form':form,'product': product})