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

        # ✅ Gmail validation
        if not re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', email):
            messages.error(request, "Email must be a valid Gmail address!")
            return redirect('/signup/')

        # ✅ Password match check
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('/signup/')

        # ✅ Username exists check
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('/signup/')

        # ✅ Email exists check (optional but good)
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect('/signup/')

        # ✅ Create user
        User.objects.create_user(username=username, email=email, password=password)

        messages.success(request, "Account created successfully!")
        return redirect('/login/')

    return render(request, 'signup.html')


# 🔐 LOGIN
def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            messages.error(request, "Invalid email")
            return redirect('/login/')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/home/')  # or your dashboard
        else:
            messages.error(request, "Invalid password")
            return redirect('/login/')

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


# 🛠 HELP
def help_support(request):
    return render(request, 'help.html')


# ⚙ SETTINGS
def settings_page(request):
    return render(request, 'settings.html')


# 📩 SEND SUPPORT
def send_support(request):
    if request.method == "POST":
        message = request.POST.get('message')

        send_mail(
            "Support Request",
            message,
            settings.EMAIL_HOST_USER,
            ["admin@example.com"],
            fail_silently=True
        )

        messages.success(request, "Message sent!")

    return redirect('/help/')


# 🛒 ADMIN DASHBOARD
from django.contrib.auth.models import User
from django.db.models import Sum
from .models import Product, Order

def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('/')

    total_users = User.objects.count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(total=Sum('total_price'))['total'] or 0

    orders = Order.objects.all().order_by('-id')
    users = User.objects.all()

    context = {
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'orders': orders,
        'users': users
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