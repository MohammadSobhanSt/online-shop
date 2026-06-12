from django.core.validators import MinValueValidator
from django.db import models
from accounts.models import CustomUser
from django.core.exceptions import ValidationError
from autoslug import AutoSlugField


class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name', unique=True, always_update=True)
    price = models.PositiveIntegerField()
    cover = models.FileField(upload_to='images/')
    product_count = models.PositiveIntegerField() # How much of that item exsists
    description = models.TextField()
    category = models.CharField(max_length=100)
    
    
    def __str__(self):
        return f"{self.name} - {self.category}"
        
    
    def is_in_stock(self, quantity=1):
        return self.product_count >= quantity
    
    def reduce_stock(self, quantity):
        if self.product_count >= quantity:
            self.product_count -= quantity
            self.save()
        else:
            raise ValidationError("You can't order more than product number...")

    
class Purchase(models.Model):
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, related_name='purchased_products') # becuase it can have no buyer but if there is any buyer we should fill the user
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchase_items')
    quantity_user_want = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)]) # How much user wants to select this product
    total_amount = models.PositiveIntegerField()
    bought_at = models.DateTimeField(auto_now_add=True)
    during_process = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.buyer} bought: {self.product.name}, during process: {self.during_process}"



class Favorite(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="favorites")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} liked \"{self.product.name}\""

