from django.db import models
from accounts.models import CustomUser
from django.core.exceptions import ValidationError


class Product(models.Model):
    name = models.CharField(max_length=100)
    buyer = models.ManyToManyField(CustomUser, blank=True, related_name='purchased_products') # becuase it can have no buyer but if there is any buyer we should fill the user
    price = models.PositiveIntegerField()
    cover = models.FileField(upload_to='images/')
    product_count = models.PositiveIntegerField() # How much of that item exsists
    quantity_user_want = models.PositiveSmallIntegerField(default=1) # How much user wants to select this product 
    description = models.TextField()
    tag = models.CharField(max_length=100)
    
    
    def __str__(self):
        return f"{self.name} - {self.tag}"
        
    
    def is_in_stock(self):
        return self.product_count > 0
    
    def reduce_stock(self):
        if self.product_count >= self.quantity_user_want:
            self.product_count -= self.quantity_user_want
            self.save()
        else:
            raise ValidationError("You can't order more than product number...")
    