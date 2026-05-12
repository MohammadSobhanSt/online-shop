from django.db import models
from accounts.models import CustomUser
from django.core.exceptions import ValidationError


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    cover = models.FileField(upload_to='images/')
    product_count = models.PositiveIntegerField() # How much of that item exsists
    description = models.TextField()
    tag = models.CharField(max_length=100)
    
    
    def __str__(self):
        return f"{self.name} - {self.tag}"
        
    
    def is_in_stock(self, quantity=1):
        return self.product_count >= quantity
    
    def reduce_stock(self, quantity):
        if self.product_count >= quantity:
            self.product_count -= quantity
            self.save()
        else:
            raise ValidationError("You can't order more than product number...")
    
    
    
class Purchase(models.Model):
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE ,blank=True, related_name='purchased_products') # becuase it can have no buyer but if there is any buyer we should fill the user
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchase_items')
    quantity_user_want = models.PositiveSmallIntegerField(default=1) # How much user wants to select this product 
    total_amount = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.buyer} bought {self.quantity_user_want} of {self.product.name}"
        