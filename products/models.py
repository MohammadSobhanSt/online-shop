from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    cover = models.FileField(upload_to='images/')
    product_count = models.PositiveIntegerField() # How much of that item exsists
    description = models.TextField()
    tag = models.CharField(max_length=100)
    
    
    def __str__(self):
        return f"{self.name} - {self.tag}"