from django.contrib import admin
from django.urls import path, include
from store import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # 🔐 ADMIN
    path('admin/', admin.site.urls),

    # 🔑 AUTH
    path('', views.login_view),
    path('login/', views.login_view),
    path('signup/', views.signup_view),
    path('logout/', views.logout_view),

    # 🏠 MAIN
    path('home/', views.home, name='home'),

    # 🛒 CART
    path('add-to-cart/', views.add_to_cart),
    path('cart/', views.cart_view),
    path('remove/<int:item_id>/', views.remove_from_cart),
    path('increase/<int:item_id>/', views.increase_qty),
    path('decrease/<int:item_id>/', views.decrease_qty),

    # 💳 PAYMENT
    path('checkout/', views.checkout, name='checkout'),
    path('upi-payment/', views.upi_payment, name='upi_payment'),
    path('payment-success/', views.payment_success, name='payment_success'),

    # 📦 ORDERS
    path('orders/', views.orders, name='orders'),
    path('track/<int:order_id>/', views.track_order, name='track_order'),
    path('cancel-order/<int:order_id>/', views.cancel_order),

    # 👤 PROFILE
    path('profile/', views.profile, name='profile'),

    # 📄 STATIC PAGES
    path('about/', views.about),
    path('contact/', views.contact),

    # 🛠 HELP & SETTINGS
    path('help/', views.help_support),
    path('send-support/', views.send_support),
    path('settings/', views.settings_page),

    # 🛒 ADMIN DASHBOARD
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('update-status/<int:order_id>/<str:status>/', views.update_status),
    path('reply/<int:id>/', views.reply_issue),

    # ✅ FIXED (only keep if function exists)
    path('resolve/<int:id>/', views.resolve_issue),

    # 📦 STOCK
    path('add-stock/<int:id>/', views.add_stock),
    path('remove-stock/<int:id>/', views.remove_stock),

    # 📄 INVOICE
    path('invoice/<int:order_id>/', views.invoice),

    # 🔐 ALLAUTH
    path('accounts/', include(('allauth.urls', 'allauth'), namespace='accounts')),

    # 🔐 OTP
    path('otp-login/', views.send_otp),
    path('verify-otp/', views.verify_otp),

    # 📧 TEST
    path('test-email/', views.test_email),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)