from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Category, Subcategory, JewelryItem, Cart, CartItem, Order, OrderItem, Review , Notices
from .serializers import CategorySerializer, SubcategorySerializer, JewelryItemSerializer, CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer, ReviewSerializer, NoticesSerializer
from .permissions import IsOwner, IsCustomer
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from .utils import send_order_confirmation_email
User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    """
    A test API endpoint that requires authentication
    """
    user = request.user
    
    return Response({
        'message': 'Hello from Django Backend!',
        'user': {
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'auth0_id': user.auth0_id,
            'role': user.role,
            'is_premium': user.is_premium,
        },
        'auth_method': 'Auth0 JWT',
        'status': 'success'
    })

@api_view(['GET'])
def public_view(request):
    """
    A public API endpoint (no authentication required)
    """
    return Response({
        'message': 'This is a public endpoint',
        'status': 'success'
    })

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Get or update user profile
    """
    user = request.user
    
    if request.method == 'GET':
        return Response({
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'profile_picture': user.profile_picture,
                'phone_number': user.phone_number,
                'date_of_birth': user.date_of_birth,
                'bio': user.bio,
                'role': user.role,
                'is_premium': user.is_premium,
                'date_joined': user.created_at,
            }
        })
    
    elif request.method == 'PUT':
        # Update user profile
        data = request.data
        if 'profile_picture' in data:
            user.profile_picture = data['profile_picture']
        if 'name' in data:
            user.name = data['name']
        if 'phone_number' in data:
            user.phone_number = data['phone_number']
        if 'date_of_birth' in data and data['date_of_birth']:
            # Handle date format from frontend
            from datetime import datetime
            try:
                if isinstance(data['date_of_birth'], str):
                    user.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
                else:
                    user.date_of_birth = data['date_of_birth']
            except ValueError:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        if 'bio' in data:
            user.bio = data['bio']
        # Role can only be updated through Django admin panel
            
        user.save()
        
        return Response({
            'message': 'Profile updated successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'phone_number': user.phone_number,
                'date_of_birth': user.date_of_birth,
                'bio': user.bio,
                'role': user.role,
            }
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_stats(request):
    """
    Get user statistics
    """
    user = request.user
    total_users = User.objects.count()
    
    return Response({
        'user_stats': {
            'total_users': total_users,
            'user_role': user.role,
            'is_premium': user.is_premium,
            'member_since': user.created_at.strftime('%B %Y'),
        }
    })

# Category

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsOwner]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['GET'])
    def get_subcategories_by_category(self, request, pk=None):
        """
        Get all subcategories for a specific category
        """
        category = self.get_object()
        subcategories = category.subcategories.all()
        if not subcategories:
            return Response({'message': 'No subcategories found for this category'}, status=404)
        serializer = SubcategorySerializer(subcategories, many=True)
        return Response(serializer.data)
    
class SubcategoryViewSet(viewsets.ModelViewSet):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsOwner]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['GET'])
    def get_jewelry_items_by_subcategory(self, request, pk=None):
        """
        Get all jewelry items for a specific subcategory
        """
        subcategory = self.get_object()
        jewelry_items = subcategory.jewelry_items.all()
        if not jewelry_items:
            return Response({'message': 'No jewelry items found for this subcategory'}, status=404)
        serializer = JewelryItemSerializer(jewelry_items, many=True)
        return Response(serializer.data)
    
class JewelryItemViewSet(viewsets.ModelViewSet):
    queryset = JewelryItem.objects.all()
    serializer_class = JewelryItemSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsOwner]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['GET'])
    def get_reviews(self, request, pk=None):
        """
        Get all reviews for a specific jewelry item
        """
        jewelry_item = self.get_object()
        reviews = jewelry_item.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsCustomer]

    def get_queryset(self):
        user = self.request.user
        # Since each user has exactly one cart, get it directly
        return Cart.objects.filter(user=user)
    
    def perform_create(self, serializer):
        # Cart creation is not allowed since it's automatic
        return Response({'error': 'Cart creation not allowed. Cart is automatically created with user.'}, 
                       status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['DELETE'])
    def clear_cart(self, request):
        """
        Clear the user's cart
        """
        user = request.user
        try:
            cart = user.cart  # Use the new related name
            cart.items.all().delete()
            return Response({'message': 'Cart cleared successfully'}, status=204)
        except Cart.DoesNotExist:
            return Response({'message': 'Cart not found'}, status=404)

class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsCustomer]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def perform_create(self, serializer):
        cart = self.request.user.cart
        serializer.save(cart=cart)

    @action(detail=True, methods=['PATCH'])
    def update_quantity(self, request, pk=None):
        """
        Update quantity of a specific cart item
        """
        try:
            item = self.get_object()
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=404)
        
        quantity = request.data.get('quantity')
        if quantity is None:
            return Response({'error': 'Quantity is required'}, status=400)

        try:
            quantity = int(quantity)
        except ValueError:
            return Response({'error': 'Quantity must be an integer'}, status=400)

        if quantity <= 0:
            item.delete()
            return Response({'message': 'Item removed as quantity was set to 0'}, status=204)

        item.quantity = quantity
        item.save()
        return Response(CartItemSerializer(item).data)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.action =='create':
            permission_classes = [IsCustomer]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        if self.request.user.role == 'owner':
            return Order.objects.all()
        else:
            return Order.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """
        Create order and automatically create order items from user's cart
        """
        user = self.request.user
        
        # Get user's cart
        cart = Cart.objects.filter(user=user).first()
        if not cart or not cart.items.exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Cannot create order: Cart is empty")
        
        # Calculate total amount from cart items
        total_amount = sum(
            item.quantity * item.jewelry_item.price 
            for item in cart.items.all()
        )
        
        # Create the order
        order = serializer.save(user=user, total_amount=total_amount)
        
        # Create order items from cart items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                jewelry_item=cart_item.jewelry_item,
                quantity=cart_item.quantity
            )
        
        # Clear the cart after successful order creation
        cart.items.all().delete()

        # Send order confirmation email
        send_order_confirmation_email(order)


    @action(detail=True, methods=['PUT'])
    def cancel(self, request, pk=None):
        """
        Cancel an order by updating status to cancelled
        """
        order = self.get_object()
        if order.user != request.user:
            return Response({'error': 'You do not have permission to cancel this order'}, status=403)
        
        if order.status != 'pending':
            return Response({'error': 'Only pending orders can be cancelled'}, status=400)
        
        # Update order status to cancelled
        order.status = 'cancelled'
        order.save()
        return Response({'message': 'Order cancelled successfully'}, status=200)

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    def get_queryset(self):
        product_id = self.request.query_params.get('product_id', None)
        if product_id is not None:
            return Review.objects.filter(jewelry_item__id=product_id)
        return Review.objects.all()

class AdminOrderViewSet(viewsets.ModelViewSet):
    """
    Admin viewset for managing all orders
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsOwner]

    @action(detail=True, methods=['PUT'])
    def update_status(self, request, pk=None):
        """
        Update order status (shipped, delivered, etc.)
        """
        order = self.get_object()
        new_status = request.data.get('status')
        
        valid_statuses = ['pending', 'completed', 'cancelled','accepted']
        if new_status not in valid_statuses:
            return Response({'error': f'Invalid status. Must be one of: {valid_statuses}'}, status=400)
        
        order.status = new_status
        order.save()
        return Response({'message': f'Order status updated to {new_status}'}, status=200)


class NoticesViewSet(viewsets.ModelViewSet):
    """
    Viewset for managing notices
    """
    queryset = Notices.objects.all()
    serializer_class = NoticesSerializer
    # permission_classes = [IsOwner]

    def perform_create(self, serializer):
        serializer.save()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsOwner]
        return [permission() for permission in permission_classes]

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def check_ip_role(request):
#     """
#     Check current IP and role assignment for debugging
#     """
#     from accounts.authentication import get_client_ip, is_owner_ip
    
#     user = request.user
#     client_ip = get_client_ip(request)
#     is_owner = is_owner_ip(client_ip)
    
#     return Response({
#         'user': {
#             'email': user.email,
#             'current_role': user.role,
#             'is_premium': user.is_premium,
#         },
#         'ip_info': {
#             'client_ip': client_ip,
#             'is_owner_ip': is_owner,
#             'should_be_owner': is_owner,
#         },
#         'message': f'User accessed from IP: {client_ip}, Role: {user.role}'
#     })

# @api_view(['GET'])
# def debug_ip(request):
#     """
#     Debug endpoint to show IP information (public access for testing)
#     """
#     from accounts.authentication import get_client_ip, is_owner_ip
    
#     client_ip = get_client_ip(request)
#     is_owner = is_owner_ip(client_ip)
    
#     # Get all headers for debugging
#     headers = {key: value for key, value in request.META.items() if key.startswith('HTTP_')}
    
#     return Response({
#         'ip_info': {
#             'client_ip': client_ip,
#             'is_owner_ip': is_owner,
#             'x_forwarded_for': request.META.get('HTTP_X_FORWARDED_FOR'),
#             'remote_addr': request.META.get('REMOTE_ADDR'),
#         },
#         'headers': headers,
#         'message': f'Your IP is: {client_ip}, Owner status: {is_owner}'
#     })

# @api_view(['POST'])
# def check_ip_role_frontend(request):
#     """
#     Check what role would be assigned for a given IP (sent from frontend)
#     """
#     from accounts.authentication import is_owner_ip
    
#     data = request.data
#     frontend_ip = data.get('ip')
    
#     if not frontend_ip:
#         return Response({
#             'error': 'IP address is required in request body'
#         }, status=400)
    
#     is_owner = is_owner_ip(frontend_ip)
#     role = 'owner' if is_owner else 'customer'
    
#     return Response({
#         'ip_info': {
#             'provided_ip': frontend_ip,
#             'is_owner_ip': is_owner,
#             'assigned_role': role,
#         },
#         'message': f'IP {frontend_ip} would be assigned role: {role}'
#     })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_role(request):
    """
    Get the current user's role
    """
    user = request.user
    return Response({
        'role': user.role
        }, status=200)

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_mail_form(request):
    """
    Send contact form email with HTML template
    """
    name = request.data.get('name')
    email = request.data.get('email')
    phone = request.data.get('phone')
    subject = request.data.get('subject')
    message = request.data.get('message')

    if not all([name, email, subject, message]):
        return Response({'error': 'All fields are required'}, status=400)

    # Render the HTML template with context
    html_message = render_to_string('email/contact_email_template.html', {
        'full_name': name,
        'email': email,
        'phone': phone,
        'subject': subject,
        'message': message
    })

    email_obj = EmailMessage(
        subject=f"New Contact Message: {subject}",
        body=html_message,
        from_email=settings.EMAIL_HOST_USER,
        to=[settings.EMAIL_HOST_USER],
    )
    email_obj.content_subtype = "html"  # Main trick to send HTML message

    try:
        email_obj.send()
        return Response({'message': 'Email sent successfully'}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

