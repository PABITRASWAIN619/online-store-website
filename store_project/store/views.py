import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Sum

from .models import Product, Cart, CartItem, Order, OrderItem, Category, Profile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

import razorpay
import requests

# 🏠 HOME
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Sum

from .models import Product, Cart, CartItem, Order, OrderItem, Category, Profile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import  SupportMessage
import requests
import razorpay

# 🏠 HOME
def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    query = request.GET.get('q')
    category_id = request.GET.get('category')
    sort = request.GET.get('sort')

    if query:
        products = products.filter(name__icontains=query)

    if category_id:
        products = products.filter(category__id=category_id)

    if sort == "low":
        products = products.order_by('price')
    elif sort == "high":
        products = products.order_by('-price')

    cart_count = 0
    profile = None

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_count = sum(item.quantity for item in CartItem.objects.filter(cart=cart))
        profile, _ = Profile.objects.get_or_create(user=request.user)

    return render(request, 'home.html', {
        'products': products,
        'categories': categories,
        'cart_count': cart_count,
        'profile': profile
    })


# 👤 PROFILE
@login_required
def profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    cart = Cart.objects.filter(user=request.user).first()
    cart_count = CartItem.objects.filter(cart=cart).count() if cart else 0

    orders_count = Order.objects.filter(user=request.user).count()

    if request.method == "POST":
        profile.phone = request.POST.get('phone')

        if request.FILES.get('image'):
            profile.image = request.FILES['image']

        profile.save()

    return render(request, 'profile.html', {
        'profile': profile,
        'cart_count': cart_count,
        'orders_count': orders_count
    })



# 🔐 SIGNUP
def signup_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Password match check
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('/signup/')

        # Username check
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('/signup/')

        # Email check
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('/signup/')

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Account created successfully!")
        return redirect('/login/')

    return render(request, 'signup.html')


# 🔐 LOGIN
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username  # Django needs username internally
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password")
            return redirect('/login/')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/home/')
        else:
            messages.error(request, "Invalid email or password")

    return render(request, 'login.html')
# 🔓 LOGOUT
def logout_view(request):
    logout(request)
    return redirect('/login/')


# 🛒 ADD TO CART
@login_required
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    product = get_object_or_404(Product, id=product_id)

    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        item.quantity += 1
        item.save()

    return redirect('/cart/')


# 🧾 CART
@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)

    total_price = sum(item.product.price * item.quantity for item in items)
    cart_count = sum(item.quantity for item in items)

    return render(request, 'cart.html', {
        'items': items,
        'total_price': total_price,
        'cart_count': cart_count
    })


# ❌ REMOVE ITEM
@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('/cart/')


# ➕ INCREASE
@login_required
def increase_qty(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.quantity += 1
    item.save()
    return redirect('/cart/')


# ➖ DECREASE
@login_required
def decrease_qty(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect('/cart/')


# 💳 CHECKOUT
@login_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)

    if not items:
        messages.error(request, "Cart is empty!")
        return redirect('/cart/')

    total = sum(item.product.price * item.quantity for item in items)

    if request.method == "POST":
        address = request.POST.get('address')
        payment = request.POST.get('payment')

        if not address:
            messages.error(request, "Enter address")
            return redirect('/checkout/')

        # COD
        if payment == "COD":
            order = Order.objects.create(
                user=request.user,
                address=address,
                total_price=total,
                status="Completed",
                payment_method="COD"
            )

            for item in items:
                OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

            items.delete()
            cart.delete()

            send_mail("Order Confirmed", f"Order #{order.id} placed", settings.EMAIL_HOST_USER, [request.user.email])

            return redirect('payment_success')

        # UPI / Card
        elif payment in ["UPI", "Card"]:
            request.session['temp_order'] = {
                'total': total,
                'address': address,
                'payment_method': payment
            }
            return redirect('upi_payment')

        # Razorpay
        elif payment == "Razorpay":
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY, settings.RAZORPAY_SECRET))
            payment_order = client.order.create({
                "amount": int(total * 100),
                "currency": "INR",
                "payment_capture": "1"
            })

            request.session['razorpay_order'] = {
                'order_id': payment_order['id'],
                'total': total,
                'address': address
            }

            return render(request, 'payment.html', {
                'order_id': payment_order['id'],
                'amount': total,
                'key': settings.RAZORPAY_KEY
            })

    return render(request, 'checkout.html', {'items': items, 'total': total})


# ✅ PAYMENT SUCCESS
@login_required
def payment_success(request):

    temp = request.session.get('temp_order')
    razor = request.session.get('razorpay_order')

    if temp or razor:
        data = temp if temp else razor

        order = Order.objects.create(
            user=request.user,
            address=data['address'],
            total_price=data['total'],
            status="Completed",
            payment_method=data.get('payment_method', 'Razorpay')
        )

        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            items = CartItem.objects.filter(cart=cart)

            for item in items:
                OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

            items.delete()
            cart.delete()

        request.session.pop('temp_order', None)
        request.session.pop('razorpay_order', None)

        send_mail("Order Confirmed", f"Order #{order.id} placed", settings.EMAIL_HOST_USER, [request.user.email])

        return render(request, 'success.html', {'order': order})

    return render(request, 'success.html')


# 📦 ORDERS
@login_required
def orders(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders.html', {'orders': user_orders})


# 🚫 CANCEL
@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status == "Pending":
        order.status = "Cancelled"
        order.save()

    return redirect('/orders/')


# 🚚 TRACK
@login_required
def track_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    progress = 0
    if order.status == "Pending":
        progress = 10
    elif order.status == "Shipped":
        progress = 60
    elif order.status == "Delivered":
        progress = 100

    return render(request, 'track.html', {'order': order, 'progress': progress})


# 🧾 INVOICE PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

@login_required
def invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()

    content = [
        Paragraph(f"Order ID: {order.id}", styles['Normal']),
        Paragraph(f"Total: ₹{order.total_price}", styles['Normal']),
        Paragraph(f"Payment: {order.payment_method}", styles['Normal']),
        Paragraph(f"Address: {order.address}", styles['Normal']),
    ]

    doc.build(content)
    return response


# 👤 PROFILE
@login_required
def profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        profile.phone = request.POST.get('phone')

        if request.FILES.get('image'):
            profile.image = request.FILES.get('image')

        if request.POST.get('delete_image'):
            profile.image = 'default.png'

        profile.save()

    return render(request, 'profile.html', {'profile': profile})


# 📥 FETCH PRODUCTS
def fetch_products(request):
    data = requests.get("https://fakestoreapi.com/products").json()

    for item in data:
        category, _ = Category.objects.get_or_create(name=item['category'])

        Product.objects.get_or_create(
            name=item['title'],
            price=item['price'],
            image=item['image'],
            category=category
        )

    return HttpResponse("Loaded")


# 📄 STATIC PAGES
def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import SupportMessage

# 🛠 HELP PAGE
@login_required
def help_support(request):
    user_messages = SupportMessage.objects.filter(user=request.user).order_by('-id')

    return render(request, 'help.html', {
        'messages': user_messages
    })


# 📩 SEND SUPPORT MESSAGE
def send_support(request):
    if request.method == "POST":
        message = request.POST.get('message')

        # ✅ Save to database
        SupportMessage.objects.create(
            user=request.user,
            message=message
        )

        # ✅ Send email to admin
        send_mail(
            "Support Request",
            message,
            settings.EMAIL_HOST_USER,
            ["admin@example.com"],
            fail_silently=True
        )

        messages.success(request, "Message sent successfully!")

    return redirect('/help/')


# ⚙ SETTINGS PAGE
def settings_page(request):
    return render(request, 'settings.html')


# 🛒 ADMIN DASHBOARD
from .models import Product, Order, SupportMessage

def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('/')

    total_users = User.objects.count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(total=Sum('total_price'))['total'] or 0

    orders = Order.objects.all().order_by('-id')
    users = User.objects.all()

    # 👉 ADD THIS HERE
    messages_data = SupportMessage.objects.all().order_by('-id')

    context = {
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'orders': orders,
        'users': users,
        'issues': messages_data   # 👉 ADD THIS
    }

    return render(request, 'admin_dashboard.html', context)

# 🔄 UPDATE ORDER STATUS
@staff_member_required
def update_status(request, order_id, status):
    order = Order.objects.get(id=order_id)
    order.status = status
    order.save()
    return redirect('/admin-dashboard/')


# 💰 UPI PAGE
@login_required
def upi_payment(request):
    temp_order = request.session.get('temp_order')

    if not temp_order:
        messages.error(request, "No payment found")
        return redirect('/checkout/')

    return render(request, 'upi_payment.html', {
        'order': {
            'id': 12345,
            'total': temp_order['total']
        }
    })
def add_stock(request, id):
    product = Product.objects.get(id=id)
    product.stock += 1
    product.save()
    return redirect('/admin-dashboard/')


def remove_stock(request, id):
    product = Product.objects.get(id=id)
    if product.stock > 0:
        product.stock -= 1
        product.save()
    return redirect('/admin-dashboard/')
import random

def send_otp(request):
    if request.method == "POST":
        email = request.POST.get('email')

        otp = str(random.randint(1000, 9999))

        request.session['otp'] = otp
        request.session['email'] = email

        send_mail(
            "Your OTP Code",
            f"Your OTP is {otp}",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False
        )

        return redirect('/verify-otp/')
import random
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect

def send_otp(request):
    if request.method == "POST":
        email = request.POST.get('email')

        otp = str(random.randint(1000, 9999))

        request.session['otp'] = otp
        request.session['email'] = email

        send_mail(
            "Your OTP Code",
            f"Your OTP is {otp}",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False
        )

        return redirect('/verify-otp/')

    return render(request, 'send_otp.html')
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse

def test_email(request):
    send_mail(
        "Test Email",
        "OTP working test",
        settings.EMAIL_HOST_USER,
        [settings.EMAIL_HOST_USER],
        fail_silently=False
    )
    return HttpResponse("Email sent")
from django.shortcuts import render, redirect

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login

def verify_otp(request):
    if request.method == "POST":
        entered = request.POST.get('otp')
        real = request.session.get('otp')
        email = request.session.get('email')

        if entered == real:
            user, _ = User.objects.get_or_create(username=email, email=email)
            login(request, user)
            return redirect('/home/')
        else:
            messages.error(request, "Invalid OTP")

    return render(request, 'verify_otp.html')
from django.core.mail import send_mail
from django.conf import settings

def reply_issue(request, id):
    issue = SupportMessage.objects.get(id=id)

    if request.method == "POST":
        reply_msg = request.POST.get('reply')

        # Save reply
        issue.reply = reply_msg
        issue.is_replied = True
        issue.save()

        # Send email to user
        send_mail(
            "Reply from Support",
            reply_msg,
            settings.EMAIL_HOST_USER,
            [issue.user.email],
            fail_silently=True
        )

        messages.success(request, "Reply sent!")

        return redirect('/admin-dashboard/')

    return render(request, 'reply.html', {'issue': issue})
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
def resolve_issue(request, id):
    issue = get_object_or_404(SupportMessage, id=id)

    issue.is_replied = True
    issue.save()

    messages.success(request, "Issue resolved successfully ✅")
    return redirect('admin_dashboard')
from django.http import JsonResponse
from .models import SupportMessage

@login_required
def get_messages(request):
    msgs = SupportMessage.objects.filter(user=request.user).order_by('id')

    data = []
    for m in msgs:
        data.append({
            'message': m.message,
            'reply': m.reply,
            'is_replied': m.is_replied
        })

    return JsonResponse({'messages': data})