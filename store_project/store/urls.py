from django.contrib import admin
from django.urls import path, include
from store import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # 🔐 ADMIN
    path('admin/', admin.site.urls),

    # 🔑 AUTH
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login_page'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    # 🏠 MAIN
    path('home/', views.home, name='home'),

    # 🛒 CART
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('increase/<int:item_id>/', views.increase_qty, name='increase_qty'),
    path('decrease/<int:item_id>/', views.decrease_qty, name='decrease_qty'),

    # 💳 CHECKOUT & PAYMENT
    path('checkout/', views.checkout, name='checkout'),
    path('upi-payment/', views.upi_payment, name='upi_payment'),
    path('payment-success/', views.payment_success, name='payment_success'),

    # 📦 ORDERS
    path('orders/', views.orders, name='orders'),
    path('track/<int:order_id>/', views.track_order, name='track_order'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),

    # 👤 PROFILE
    path('profile/', views.profile, name='profile'),

    # 📄 STATIC PAGES
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # 🛠 HELP & SETTINGS
    path('help/', views.help_support, name='help'),
    path('send-support/', views.send_support, name='send_support'),
    path('settings/', views.settings_page, name='settings'),

    # 🛠 ADMIN DASHBOARD
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('update-status/<int:order_id>/<str:status>/', views.update_status, name='update_status'),
    path('reply/<int:id>/', views.reply_issue, name='reply_issue'),
    path('resolve/<int:id>/', views.resolve_issue, name='resolve_issue'),

    # 📦 STOCK MANAGEMENT
    path('add-stock/<int:id>/', views.add_stock, name='add_stock'),
    path('remove-stock/<int:id>/', views.remove_stock, name='remove_stock'),

    # 🧾 INVOICE
    path('invoice/<int:order_id>/', views.invoice, name='invoice'),

    # 🔐 ALLAUTH
    path('accounts/', include('allauth.urls')),

    # 🔐 OTP
    path('otp-login/', views.send_otp, name='otp_login'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),

    # 📧 TEST EMAIL
    path('test-email/', views.test_email, name='test_email'),
]

# 📂 MEDIA FILES
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)