from django.db import models

class Color(models.Model):
    name = models.CharField(max_length=50)  
    hex_code = models.CharField(max_length=7)
    
    def __str__(self):
        return self.name
    
class Size(models.Model):
    name = models.CharField(max_length=10)
    
    def __str__(self):
        return self.name
    
class SizeGroup(models.Model):
    name = models.CharField(max_length=50)  
    sizes = models.ManyToManyField(Size)
    
    def __str__(self):
        sizes_str = ', '.join([size.name for size in self.sizes.all()])
        return f"({sizes_str})"
    
class Product(models.Model):
    
    PRODUCT_TYPES = (
    ('JEANS', 'Jeans'),
    ('TSHIRT', 'T-Shirt'),
    ) 
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    design_number = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=50, choices=PRODUCT_TYPES) 
    colors = models.ManyToManyField('Color')
    available_size_groups = models.ManyToManyField(SizeGroup)
    current_stock = models.IntegerField(default=0)
    mrp = models.DecimalField(max_digits=8, decimal_places=2) 
    dealer_price = models.DecimalField(max_digits=8, decimal_places=2) 
    
    def __str__(self):
        return self.title
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.product.title} - {self.image.url}"
