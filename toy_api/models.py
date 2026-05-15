from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField
import shortuuid

class User(AbstractUser):
    username = models.CharField(unique=True, max_length=150)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        if self.email:
            base_username = self.email.split("@")[0]
        else:
            base_username = "user"

        if not self.full_name:
            self.full_name = base_username

        if not self.username:
            self.username = base_username
            counter = 1
            while User.objects.filter(username=self.username).exists():
                self.username = f"{base_username}{counter}"
                counter += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    image = models.ImageField(upload_to="profile_images", default="default/default-user.jpg", null=True, blank=True)
    full_name = models.CharField(max_length=150, null=True, blank=True)
    location = models.CharField(max_length=250, null=True, blank=True)
    country = models.CharField(max_length=60, null=True, blank=True)
    cell = PhoneNumberField(region='BD', blank=True, null=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = self.user.full_name
        super().save(*args, **kwargs)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


class Category(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    class Meta:
        verbose_name_plural = "Category"
    def product_count(self):
        return Product.objects.filter(category=self).count()


class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product_name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    min_age = models.PositiveIntegerField()
    max_age = models.PositiveIntegerField(null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Product"

    def __str__(self):
        return self.product_name

    def clean(self):
        if self.max_age is not None and self.min_age > self.max_age:
            raise ValidationError({'max_age': 'Max age must be >= min age'})

    def save(self, *args, **kwargs):
        self.clean()
        if not self.slug:
            self.slug = f"{slugify(self.product_name)}-{shortuuid.uuid()[:4]}"
        super().save(*args, **kwargs)

    @property
    def in_stock(self):
        return self.stock > 0


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    img = models.ImageField(upload_to='productsImage')


class Cart(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name='cart')
    session_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.profile:
            return f"{self.profile.user.username}'s Cart"
        return f"Cart {self.session_id}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.product.product_name} x {self.quantity}"

    @property
    def total_price(self):
        return self.price * self.quantity


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    )

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='orders')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()
    phone = PhoneNumberField(region='BD', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.profile.full_name}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @classmethod
    def create_from_cart(cls, cart, shipping_address, phone=None):
        if not cart.items.exists():
            raise ValueError("Cannot create order from an empty cart")

        if not cart.profile:
            raise ValueError("Cart must be associated with a logged-in user")

        order = cls.objects.create(
            profile=cart.profile,
            total=cart.total_price,
            shipping_address=shipping_address,
            phone=phone or cart.profile.cell
        )

        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                unit_price=cart_item.price
            )
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save(update_fields=['stock'])

        cart.items.all().delete()
        return order


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.product_name} x {self.quantity}"

    @property
    def total_price(self):
        return self.unit_price * self.quantity
    
