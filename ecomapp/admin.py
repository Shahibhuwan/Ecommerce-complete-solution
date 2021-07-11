from ecomapp.models import Cart, CartProduct, Category,Admin, Customer, Order, Product, ProductImage
from django.contrib import admin

# Register your models here.
admin.site.register(
    [ Admin, Customer, Category, Product, Cart, CartProduct, Order, ProductImage])
