from django.shortcuts import render
from django.views import View
from .models import Product


class ProductListView(View):
    template_name = 'products/product_list.html'
    
    def get(self, request):
        products = Product.objects.all()
        return render(request, self.template_name, {'products':products})