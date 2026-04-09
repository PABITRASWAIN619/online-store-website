from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem
from .models import Profile
admin.site.register(Profile)

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)