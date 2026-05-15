from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework_simplejwt.tokens import Token

from toy_api.models import User, Profile, Category, Product, Cart, CartItem, Order, OrderItem, ProductImage

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token= super().get_token(user)
        token['full_name']=user.full_name
        token['email']=user.email
        token['username']=user.username
        return token
    

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    location = serializers.CharField(write_only=True, required=False, allow_blank=True)
    country = serializers.CharField(write_only=True, required=False, allow_blank=True)
    cell = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password', 'password2', 'location', 'country', 'cell']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match"})
        return data

    def create(self, validated_data):  

        user = User.objects.create(
            full_name=validated_data['full_name'],
            email=validated_data['email']
        )
        user.username = user.email.split("@")[0]
        user.set_password(validated_data['password'])
        user.save()
        profile = user.profile   # get the auto-created profile
        profile.location = validated_data.get('location', '')
        profile.country = validated_data.get('country', '')
        profile.cell = validated_data.get('cell', '')
        profile.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    class  Meta:
        model=User
        fields='__all__' 
class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    is_staff = serializers.BooleanField(source='user.is_staff', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'user_id', 'full_name', 'location', 'country', 'cell', 'email', 'is_staff']
class CategorySerializer(serializers.ModelSerializer):
    def get_product_count(self, category):
        return category.products.count()
    class Meta:
        model=Category
        fields=['id', 'title', 'slug', 'product_count']

class ProductImageSerializer(serializers.ModelSerializer):
    img_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'img', 'img_url']

    def get_img_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.img.url)
        return obj.img.url  

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, required=False)
    category_title = serializers.CharField(source='category.title',default='', read_only=True)
    category_detail = CategorySerializer(source='category', read_only=True)  # optional, for nested info

    class Meta:
        model = Product
        fields = [
            'id', 'user', 'product_name', 'category', 'category_title', 'category_detail',
            'description', 'price', 'stock', 'is_available', 'min_age', 'max_age',
            'slug', 'created_at', 'updated_at', 'images'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'user', 'category_detail']
        # 'category' is writable (expects an ID)
        extra_kwargs = {
            'category': {'required': False, 'allow_null': True}
        }

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        validated_data.setdefault('is_available', True)
        product = Product.objects.create(**validated_data)
        for image_data in images_data:
            ProductImage.objects.create(product=product, **image_data)
        return product

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', None)
        instance = super().update(instance, validated_data)
        if images_data is not None:
            instance.images.all().delete()
            for image_data in images_data:
                ProductImage.objects.create(product=instance, **image_data)
        return instance
    
    

    def validate(self, data):
        min_age = data.get('min_age')
        max_age = data.get('max_age')
        if max_age is not None and min_age > max_age:
            raise serializers.ValidationError(
                {'max_age': 'Max age must be >= min age'}
            )
        return data

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model=Cart
        fields=['profile', 'session_id', 'created_at']


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=CartItem
        fields=['cart', 'product', 'quantity', 'price', 'total_price']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price', 'total_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'profile', 'total', 'status', 'shipping_address', 'phone', 'created_at', 'items']

class DashboardStatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_products = serializers.IntegerField()
    total_orders = serializers.IntegerField()
    total_categories = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    recent_orders = serializers.ListField(child=serializers.DictField())
   