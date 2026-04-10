from django.contrib import admin
from django.urls import path
from store import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # AUTH
    path('', views.login_view),
    path('login/', views.login_view),
    path('signup/', views.signup_view),
    path('logout/', views.logout_view),

    # MAIN
    path('home/', views.home, name='home'),

    # CART
    path('add-to-cart/', views.add_to_cart),
    path('cart/', views.cart_view),
    path('remove/<int:item_id>/', views.remove_from_cart),
    path('increase/<int:item_id>/', views.increase_qty),
    path('decrease/<int:item_id>/', views.decrease_qty),

    # CHECKOUT / PAYMENT
    path('checkout/', views.checkout, name='checkout'),
    path('upi-payment/', views.upi_payment, name='upi_payment'),
    path('payment-success/', views.payment_success, name='payment_success'),

    # ORDERS
    path('orders/', views.orders, name='orders'),
    path('track/<int:order_id>/', views.track_order, name='track_order'),
    path('cancel-order/<int:order_id>/', views.cancel_order),

    # PROFILE
    path('profile/', views.profile, name='profile'),

    # EXTRA
    path('fetch-products/', views.fetch_products),
    path('about/', views.about),
    path('contact/', views.contact),
    path('help/', views.help_support),
    path('settings/', views.settings_page),

    # ADMIN
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('update-status/<int:order_id>/<str:status>/', views.update_status),

    # INVOICE
    path('invoice/<int:order_id>/', views.invoice),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)