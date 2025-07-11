#!/usr/bin/env python3
"""
Script to populate the jewelry store with sample data
"""
import os
import sys
import django

# Setup Django environment
sys.path.append('/home/kisuke/Desktop/project/Full_Stack/Backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import Category, Subcategory, JewelryItem

def populate_data():
    # Create Categories
    categories_data = [
        {"name": "Rings", "description": "Beautiful rings for every occasion"},
        {"name": "Necklaces", "description": "Elegant necklaces and pendants"},
        {"name": "Bracelets", "description": "Stylish bracelets and bangles"},
        {"name": "Earrings", "description": "Beautiful earrings and studs"},
    ]
    
    categories = {}
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data["name"],
            defaults={"description": cat_data["description"]}
        )
        categories[cat_data["name"]] = category
        print(f"{'Created' if created else 'Found'} category: {category.name}")
    
    # Create Subcategories
    subcategories_data = [
        {"name": "Wedding Rings", "category": "Rings"},
        {"name": "Engagement Rings", "category": "Rings"},
        {"name": "Fashion Rings", "category": "Rings"},
        {"name": "Gold Necklaces", "category": "Necklaces"},
        {"name": "Silver Necklaces", "category": "Necklaces"},
        {"name": "Pearl Necklaces", "category": "Necklaces"},
        {"name": "Gold Bracelets", "category": "Bracelets"},
        {"name": "Silver Bracelets", "category": "Bracelets"},
        {"name": "Charm Bracelets", "category": "Bracelets"},
        {"name": "Stud Earrings", "category": "Earrings"},
        {"name": "Hoop Earrings", "category": "Earrings"},
        {"name": "Drop Earrings", "category": "Earrings"},
    ]
    
    subcategories = {}
    for sub_data in subcategories_data:
        category = categories[sub_data["category"]]
        subcategory, created = Subcategory.objects.get_or_create(
            name=sub_data["name"],
            category=category
        )
        subcategories[sub_data["name"]] = subcategory
        print(f"{'Created' if created else 'Found'} subcategory: {subcategory.name}")
    
    # Create Sample Products
    products_data = [
        {
            "name": "Classic Gold Wedding Band",
            "description": "Timeless 14k gold wedding band with smooth finish",
            "price": 899.99,
            "category": "Rings",
            "subcategory": "Wedding Rings",
            "weight": 4.5,
            "image_url": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=400"
        },
        {
            "name": "Diamond Solitaire Ring",
            "description": "Elegant 1 carat diamond engagement ring in platinum setting",
            "price": 2499.99,
            "category": "Rings",
            "subcategory": "Engagement Rings",
            "weight": 3.2,
            "image_url": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=400"
        },
        {
            "name": "Vintage Style Fashion Ring",
            "description": "Art deco inspired ring with cubic zirconia stones",
            "price": 149.99,
            "category": "Rings",
            "subcategory": "Fashion Rings",
            "weight": 2.8,
            "image_url": "https://images.unsplash.com/photo-1506630448388-4e683c67ddb0?w=400"
        },
        {
            "name": "Gold Chain Necklace",
            "description": "18k gold chain necklace, 18 inches",
            "price": 599.99,
            "category": "Necklaces",
            "subcategory": "Gold Necklaces",
            "weight": 12.5,
            "image_url": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=400"
        },
        {
            "name": "Sterling Silver Pendant",
            "description": "Beautiful silver pendant with heart design",
            "price": 89.99,
            "category": "Necklaces",
            "subcategory": "Silver Necklaces",
            "weight": 5.2,
            "image_url": "https://images.unsplash.com/photo-1506630448388-4e683c67ddb0?w=400"
        },
        {
            "name": "Pearl Strand Necklace",
            "description": "Classic white freshwater pearl necklace",
            "price": 299.99,
            "category": "Necklaces",
            "subcategory": "Pearl Necklaces",
            "weight": 15.0,
            "image_url": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=400"
        },
        {
            "name": "Gold Tennis Bracelet",
            "description": "Elegant gold tennis bracelet with crystal stones",
            "price": 799.99,
            "category": "Bracelets",
            "subcategory": "Gold Bracelets",
            "weight": 8.5,
            "image_url": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=400"
        },
        {
            "name": "Silver Cuff Bracelet",
            "description": "Modern sterling silver cuff with geometric design",
            "price": 129.99,
            "category": "Bracelets",
            "subcategory": "Silver Bracelets",
            "weight": 15.2,
            "image_url": "https://images.unsplash.com/photo-1506630448388-4e683c67ddb0?w=400"
        },
        {
            "name": "Diamond Stud Earrings",
            "description": "Classic diamond stud earrings in white gold",
            "price": 1299.99,
            "category": "Earrings",
            "subcategory": "Stud Earrings",
            "weight": 1.5,
            "image_url": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=400"
        },
        {
            "name": "Gold Hoop Earrings",
            "description": "Medium size gold hoop earrings, perfect for everyday wear",
            "price": 199.99,
            "category": "Earrings",
            "subcategory": "Hoop Earrings",
            "weight": 3.8,
            "image_url": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=400"
        }
    ]
    
    for product_data in products_data:
        category = categories[product_data["category"]]
        subcategory = subcategories[product_data["subcategory"]]
        
        product, created = JewelryItem.objects.get_or_create(
            name=product_data["name"],
            defaults={
                "description": product_data["description"],
                "price": product_data["price"],
                "category": category,
                "subcategory": subcategory,
                "weight": product_data["weight"],
                "image_url": product_data["image_url"]
            }
        )
        print(f"{'Created' if created else 'Found'} product: {product.name}")
    
    print("\nData population completed!")
    print(f"Total Categories: {Category.objects.count()}")
    print(f"Total Subcategories: {Subcategory.objects.count()}")
    print(f"Total Products: {JewelryItem.objects.count()}")

if __name__ == "__main__":
    populate_data()
