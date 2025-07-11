from django.db import models
import uuid
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import PermissionDenied
# Create your models here.

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Check if slug already exists for other categories
            if Category.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                from django.core.exceptions import ValidationError
                raise ValidationError(f"A category with slug '{self.slug}' already exists.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Subcategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Subcategories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Check if slug already exists for other subcategories
            if Subcategory.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                from django.core.exceptions import ValidationError
                raise ValidationError(f"A subcategory with slug '{self.slug}' already exists.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class JewelryItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, related_name='jewelry_items', on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, related_name='jewelry_items', on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    # stock_quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Jewelry Items"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Handle duplicate slugs
            original_slug = self.slug
            counter = 1
            while JewelryItem.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(get_user_model(), related_name='cart', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def delete(self, *args, **kwargs):
        # Prevent cart deletion
        raise PermissionDenied("Carts cannot be deleted. They are permanently linked to users.")
    
    def __str__(self):
        return f"Cart for User {self.user}"

class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    jewelry_item = models.ForeignKey(JewelryItem, related_name='cart_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ['cart', 'jewelry_item']

    def __str__(self):
        return f"CartItem {self.id} in Cart for User {self.cart.user}"

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), related_name='orders', on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} for User {self.user}"

class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    jewelry_item = models.ForeignKey(JewelryItem, related_name='order_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"OrderItem {self.id} in Order {self.order.id}"

class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), related_name='reviews', on_delete=models.CASCADE)
    jewelry_item = models.ForeignKey(JewelryItem, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'jewelry_item']

    def __str__(self):
        return f"Review {self.id} for Item {self.jewelry_item.name} by User {self.user}"

# Signal to automatically create a cart when a user is created
@receiver(post_save, sender=get_user_model())
def create_user_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)

class Notices(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    notice_type =models.CharField(max_length=20, choices=[
        ('offer', 'Offer'),
        ('notice', 'Notice'),
        ('price change', 'Price Change'),
    ], default='info')

   