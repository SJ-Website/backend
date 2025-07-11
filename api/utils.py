# shop/utils.py

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.timezone import localtime
from .models import Order, OrderItem

def send_order_confirmation_email(order):
    """
    Send an order confirmation email to the user
    """
    user = order.user
    name = user.name
    email = user.email
    order_items = OrderItem.objects.filter(order=order)
    created_at = localtime(order.created_at)

    html_message = render_to_string('email/order_confirmation.html', {
        'name': name,
        'order_id': order.id,
        'order_date': created_at.strftime('%Y-%m-%d %H:%M'),
        'items': order_items,
        'total': order.total_amount,
    })

    email_obj = EmailMessage(
        subject='Order Confirmation - Your Jewellery Order',
        body=html_message,
        from_email=settings.EMAIL_HOST_USER,
        to=[email],
    )
    email_obj.content_subtype = "html"

    try:
        email_obj.send()
        return True
    except Exception as e:
        print("Email sending failed:", str(e))
        return False
