from django.contrib import admin
from toy_api.models import User, Profile, Product, Cart, CartItem, Category,Order, OrderItem,ProductImage


admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)