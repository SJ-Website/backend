from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our ViewSets
router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'subcategories', views.SubcategoryViewSet, basename='subcategory')
router.register(r'products', views.JewelryItemViewSet, basename='jewelryitem')
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'cart-items', views.CartItemViewSet, basename='cartitem')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'reviews', views.ReviewViewSet, basename='review')
router.register(r'admin/orders', views.AdminOrderViewSet, basename='admin-order')
router.register(r'notices', views.NoticesViewSet, basename='notice')
urlpatterns = [
    path('', include(router.urls)),
    
    # Function-based or APIView-based views
    # path('protected/', views.protected_view, name='protected'),
    # path('public/', views.public_view, name='public'),
    path('profile/', views.user_profile, name='user_profile'),
    # path('stats/', views.user_stats, name='user_stats'),
    # path('check-ip-role/', views.check_ip_role, name='check_ip_role'),
    # path('debug-ip/', views.debug_ip, name='debug_ip'),
    # path('check-ip-frontend/', views.check_ip_role_frontend, name='check_ip_role_frontend'),
    path('send-email/', views.send_mail_form, name='send_email'),    
    # Role API (function-based view)
    path('role/', views.get_user_role, name='get_user_role'),
    # path('role/update/', views.update_user_role, name='update_user_role'),  # optional
]
