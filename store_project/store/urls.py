from django.contrib import admin
from django.urls import path
from store import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.login_view),

    path('home/', views.home, name='home'),
    path('add-to-cart/', views.add_to_cart),
    path('cart/', views.cart_view),
    path('checkout/', views.checkout, name='checkout'),  # ✅ Added name

    path('remove/<int:item_id>/', views.remove_from_cart),
    path('increase/<int:item_id>/', views.increase_qty),
    path('decrease/<int:item_id>/', views.decrease_qty),

    path('fetch-products/', views.fetch_products),

    path('about/', views.about),
    path('contact/', views.contact),

    path('login/', views.login_view),
    path('signup/', views.signup_view),
    path('logout/', views.logout_view),

    path('orders/', views.orders, name='orders'),  
    path('track/<int:order_id>/', views.track_order, name='track_order'),

    path('invoice/<int:order_id>/', views.invoice),
    path('payment-success/', views.payment_success, name='payment_success'),  # ✅ Removed duplicate

    path('profile/', views.profile),
    path('admin-dashboard/', views.admin_dashboard),

    # CANCEL ORDER
    path('cancel-order/<int:order_id>/', views.cancel_order),
    path('checkout/', views.checkout, name='checkout'),
    path('upi-payment/', views.upi_payment, name='upi_payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
    # ... other paths
    path('help/', views.help_support, name='help'),
path('settings/', views.settings_page, name='settings'),
path('send-support/', views.send_support, name='send_support'),
path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
path('update-status/<int:order_id>/<str:status>/', views.update_status, name='update_status'),
path('invoice/<int:order_id>/', views.invoice, name='invoice'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)