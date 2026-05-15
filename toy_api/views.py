from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.db.models import Sum, Count
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime
from django.core.mail import EmailMessage
import traceback

import json
import random
from toy_api.serializers import (
    MyTokenObtainPairSerializer,
    RegisterSerializer,
    UserSerializer,
    ProfileSerializer,
    CategorySerializer,
    ProductSerializer,
    ProductImageSerializer,
    CartSerializer,
    OrderSerializer,
    DashboardStatsSerializer,
)
from toy_api.models import (
    User,
    Profile,
    Category,
    Product,
    ProductImage,
    Cart,
    CartItem,
    Order,
    OrderItem,
)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


class ProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    lookup_field = 'user_id'

    def get_object(self):
        user_id = self.kwargs['user_id']
        profile, _ = Profile.objects.select_related('user').get_or_create(user_id=user_id)
        return profile


class ProfileUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    lookup_field = 'user_id'

    def get_object(self):
        user_id = self.kwargs['user_id']
        if self.request.user.id != user_id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only edit your own profile.")
        profile, _ = Profile.objects.select_related('user').get_or_create(user_id=user_id)
        return profile

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            full_name = request.data.get('full_name')
            if full_name and instance.user.full_name != full_name:
                instance.user.full_name = full_name
                instance.user.save(update_fields=['full_name'])

            return Response(serializer.data)
        except Exception as e:
            traceback.print_exc()
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CategoryListApiView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Category.objects.all()


class ProductCategoryListAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        category_slug = self.kwargs["category_slug"]
        return Product.objects.filter(
            category__slug=category_slug,
            is_available=True
        ).select_related('category').prefetch_related('images')


class ProductListAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        base_qs = Product.objects.select_related('category').prefetch_related('images')
        if self.request.user and self.request.user.is_staff:
            return base_qs
        return base_qs.filter(is_available=True)


class CartListApiView(generics.ListAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(profile__user=self.request.user).select_related('profile')


class OrderListApiView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            profile__user=self.request.user
        ).select_related('profile__user').prefetch_related(
            'items__product__images'
        ).order_by('-created_at')


class UserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.none()


class UserUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({"error": "Only staff can update users."}, status=403)
        return super().update(request, *args, **kwargs)


class UserDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({"error": "Only staff can delete users."}, status=403)
        user = self.get_object()
        if user == request.user:
            return Response({"error": "You cannot delete your own account."}, status=400)
        user.delete()
        return Response({"message": "User deleted successfully."}, status=200)


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.is_staff:
            return Response({"error": "Unauthorised Login"}, status=403)

        total_users = User.objects.count()
        total_products = Product.objects.count()
        total_orders = Order.objects.count()
        total_categories = Category.objects.count()
        total_revenue = Order.objects.aggregate(total=Sum('total'))['total'] or 0

        recent_orders = list(
            Order.objects.select_related('profile__user')
            .order_by('-created_at')[:5]
            .values('id', 'total', 'status', 'created_at')
        )

        data = {
            "total_users": total_users,
            "total_products": total_products,
            "total_orders": total_orders,
            "total_categories": total_categories,
            "total_revenue": total_revenue,
            "recent_orders": recent_orders,
        }

        serializer = DashboardStatsSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class DashboardProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        return Product.objects.filter(user_id=user_id).select_related('category').prefetch_related('images').order_by("-id")


class DashboardProductCreateApi(generics.CreateAPIView):
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if not request.user.is_staff and "user_id" in request.data:
            return Response(
                {"error": "Only staff can assign a different user."},
                status=status.HTTP_403_FORBIDDEN,
            )

        mutable_data = request.data.copy()

        if "user_id" not in request.data:
            mutable_data["user"] = request.user.id
        else:
            user_id = request.data.get("user_id")
            if not User.objects.filter(id=user_id).exists():
                return Response(
                    {"user_id": "User does not exist."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            mutable_data["user"] = user_id
            mutable_data.pop("user_id", None)

        category_id = mutable_data.get("category")
        if category_id and not Category.objects.filter(id=category_id).exists():
            return Response(
                {"category": "Category does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        images = request.FILES.getlist('images')
        if images:
            mutable_data['images'] = images

        serializer = self.get_serializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            {"message": "Product created successfully.", "product": serializer.data},
            status=status.HTTP_201_CREATED,
        )

    def perform_create(self, serializer):
        serializer.save()


class DashboardProductUpdateApi(generics.UpdateAPIView):
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        product = self.get_object()

        if not request.user.is_staff and product.user.id != request.user.id:
            return Response(
                {"error": "You do not have permission to update this product."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if "user_id" in request.data:
            if not request.user.is_staff:
                return Response(
                    {"error": "Only staff can reassign product to another user."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            user_id = request.data.get("user_id")
            if not User.objects.filter(id=user_id).exists():
                return Response(
                    {"user_id": "User does not exist."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            request.data._mutable = True
            request.data["user"] = user_id
            del request.data["user_id"]
            request.data._mutable = False

        category_id = request.data.get("category")
        if category_id and not Category.objects.filter(id=category_id).exists():
            return Response(
                {"category": "Category does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(product, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if "images" in request.data:
            images_data = (
                request.data.getlist("images")
                if hasattr(request.data, "getlist")
                else request.data.get("images", [])
            )
            if images_data:
                ProductImage.objects.filter(product=product).delete()
                for image_data in images_data:
                    ProductImage.objects.create(product=product, img=image_data)

        return Response(
            {"message": "Product updated successfully.", "product": serializer.data},
            status=status.HTTP_200_OK,
        )

    def perform_update(self, serializer):
        serializer.save()


class DashboardProductDeleteApi(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()
    lookup_field = "id"

    def destroy(self, request, *args, **kwargs):
        product = self.get_object()

        if not request.user.is_staff and product.user.id != request.user.id:
            return Response(
                {"error": "You do not have permission to delete this product."},
                status=status.HTTP_403_FORBIDDEN,
            )

        product.images.all().delete()
        self.perform_destroy(product)

        return Response(
            {"message": "Product deleted successfully."}, status=status.HTTP_200_OK
        )


class AdminOrderListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.select_related('profile__user').prefetch_related(
                'items__product__images'
            ).order_by('-created_at')
        return Order.objects.none()


class AdminOrderUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({"error": "Only staff can update orders."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        profile = user.profile

        items_data = request.data.get('items', [])
        if not items_data:
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        shipping_address = request.data.get('shipping_address')
        phone = request.data.get('phone')
        if not shipping_address or not phone:
            return Response({"error": "Missing shipping address or phone"}, status=status.HTTP_400_BAD_REQUEST)

        product_ids = [item['id'] for item in items_data]
        products = {p.id: p for p in Product.objects.select_related('category').filter(id__in=product_ids)}
        missing = set(product_ids) - set(products.keys())
        if missing:
            return Response({"error": f"Products not found: {missing}"}, status=400)

        order = Order.objects.create(
            profile=profile,
            total=0,
            shipping_address=shipping_address,
            phone=phone,
            status='pending'
        )

        order_items = []
        total = 0
        for item_data in items_data:
            product = products[item_data['id']]
            quantity = int(item_data['quantity'])
            unit_price = product.price
            item_total = unit_price * quantity
            total += item_total
            order_items.append(OrderItem(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=unit_price
            ))
            product.stock -= quantity
            product.save(update_fields=['stock'])

        OrderItem.objects.bulk_create(order_items)
        order.total = total
        order.save(update_fields=['total'])

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def contact_email(request):
    try:
        name = request.data.get('name')
        email = request.data.get('email')
        message = request.data.get('message')

        if not all([name, email, message]):
            return Response(
                {'error': 'All fields are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        full_message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
        send_mail(
            subject=f"Contact from {name}",
            message=full_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['islamohidul856mi647360@gmail.com'],
            fail_silently=False,
        )
        return Response(
            {'message': 'Email sent successfully!'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_order_email(request):
    user_email = request.data.get('email')
    order = request.data.get('order')
    if not user_email or not order:
        return Response({"error": "Missing email or order data"}, status=400)

    subject = f"Order Confirmation #{order['id']}"
    message = f"""
    Hello {order.get('userName', 'Customer')},

    Thank you for your order!

    Order ID: {order['id']}
    Total: {order['total']} BDT
    Delivery Address: {order['address']}
    Phone: {order['phone']}

    Items:
    """
    for item in order['items']:
        message += f"\n- {item['product_name']} x{item['quantity']} = {item['price'] * item['quantity']} BDT"
    message += "\n\nYour order will be processed soon.\n\nToyee Team"

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        return Response({"message": "Email sent successfully"})
    except Exception as e:
        return Response({"error": str(e)}, status=500)