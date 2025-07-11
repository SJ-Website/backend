from django.contrib import admin
from .models import Category, Subcategory, JewelryItem, Cart, CartItem, Order, OrderItem, Review, Notices

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name',)
    list_filter = ('category',)
@admin.register(JewelryItem)
class JewelryItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price',  'category', 'subcategory', 'created_at', 'updated_at','weight', 'is_active')
    search_fields = ('name', 'description')
    list_filter = ('category', 'subcategory','weight')
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__email',)
    list_filter = ('created_at', 'updated_at')
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'jewelry_item', 'quantity')
    search_fields = ('cart__user__email', 'jewelry_item__name')
    list_filter = ('cart', 'jewelry_item')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_amount', 'created_at', 'updated_at', 'status')
    search_fields = ('user__email',)
    list_filter = ('created_at', 'updated_at', 'status')
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'jewelry_item', 'quantity')
    search_fields = ('order__user__email', 'jewelry_item__name')
    list_filter = ('order', 'jewelry_item')
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'jewelry_item', 'rating', 'comment', 'created_at')
    search_fields = ('user__email', 'jewelry_item__name', 'comment')
    list_filter = ('rating', 'created_at')


@admin.register(Notices)
class NoticesAdmin(admin.ModelAdmin):
    list_display = ('message', 'created_at')
    search_fields = ('message',)
    ordering = ('-created_at',)