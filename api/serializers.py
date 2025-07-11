from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Category, Subcategory, JewelryItem, Cart, CartItem, Order, OrderItem, Review, Notices

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug']

    def validate_slug(self, value):
        if not value.replace('-', '').replace('_', '').isalnum():
            raise serializers.ValidationError("Slug must be alphanumeric (use hyphens or underscores if needed).")
        return value


class SubcategorySerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'category', 'slug']

    def validate(self, data):
        name = data.get('name')
        category = data.get('category')
        if self.instance:
            if Subcategory.objects.exclude(id=self.instance.id).filter(name=name, category=category).exists():
                raise serializers.ValidationError("Subcategory name must be unique within the category.")
        else:
            if Subcategory.objects.filter(name=name, category=category).exists():
                raise serializers.ValidationError("Subcategory name must be unique within the category.")
        return data


class JewelryItemSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    subcategory = serializers.PrimaryKeyRelatedField(queryset=Subcategory.objects.all())

    class Meta:
        model = JewelryItem
        fields = ['id', 'name', 'description', 'price', 'category', 'subcategory', 'image_url','weight',
                  'slug', 'created_at', 'updated_at', 'is_active']

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Jewelry item name cannot be empty.")
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be a positive number.")
        return value


class CartItemSerializer(serializers.ModelSerializer):
    jewelry_item_id = serializers.PrimaryKeyRelatedField(
        source='jewelry_item',
        queryset=JewelryItem.objects.all(),
        write_only=True
    )
    jewelry_item = JewelryItemSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'jewelry_item', 'jewelry_item_id', 'quantity']
        read_only_fields = ['cart']


    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be a positive number.")
        return value


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'updated_at', 'items']


class OrderItemSerializer(serializers.ModelSerializer):
    jewelry_item = JewelryItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'jewelry_item', 'quantity']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be a positive number.")
        return value


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'total_amount', 'created_at', 'updated_at', 'items', 'status']
        read_only_fields = ['user', 'total_amount', 'created_at', 'updated_at', 'items', 'status']

    def validate_total_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Total amount must be a positive number.")
        return value




class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    jewelry_item = serializers.PrimaryKeyRelatedField(queryset=JewelryItem.objects.all())
    rating = serializers.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        model = Review
        fields = ['id', 'user', 'jewelry_item', 'rating', 'comment', 'created_at']

    def validate_comment(self, value):
        if value and len(value.strip()) < 5:
            raise serializers.ValidationError("Comment must be at least 5 characters long.")
        return value


class NoticesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notices
        fields = ['id', 'message', 'created_at', 'notice_type']

    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty.")
        return value