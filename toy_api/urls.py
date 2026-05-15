from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from toy_api.views import (
    MyTokenObtainPairView,
    RegisterView,
    ProfileView,
    ProfileUpdateView,
    CategoryListApiView,
    ProductCategoryListAPIView,
    ProductListAPIView,  # note: correct capitalization
    CartListApiView,
    OrderListApiView,
    DashboardStatsView,
    DashboardProductListView,
    DashboardProductCreateApi,
    DashboardProductUpdateApi,
    DashboardProductDeleteApi,
    UserDeleteView,
    UserListView,
    UserUpdateView,
    contact_email,
    send_order_email,
    AdminOrderListView,
    AdminOrderUpdateView,
    CreateOrderView,
)

urlpatterns = [
    # Authentication
    path("user/token/", MyTokenObtainPairView.as_view(), name="token_obtain"),
    path("user/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("user/register/", RegisterView.as_view(), name="register"),
    path("user/profile/<int:user_id>/", ProfileView.as_view(), name="profile"),
    path(
        "user/profile/update/<int:user_id>/",
        ProfileUpdateView.as_view(),
        name="profile-update",
    ),
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/<int:id>/update/", UserUpdateView.as_view(), name="user_update"),
    path("users/<int:id>/delete/", UserDeleteView.as_view(), name="user_delete"),
    # Products & Categories
    path("products/", ProductListAPIView.as_view(), name="product_list"),
    path(
        "products/category/list/", CategoryListApiView.as_view(), name="category_list"
    ),
    path(
        "products/category/product/<slug:category_slug>/",
        ProductCategoryListAPIView.as_view(),
        name="product_by_category",
    ),  
    path("carts/", CartListApiView.as_view(), name="cart_list"),
    path("orders/", OrderListApiView.as_view(), name="order_list"),
    path('orders/create/', CreateOrderView.as_view(), name='create_order'),
    path('admin/orders/', AdminOrderListView.as_view(), name='admin_orders'),
    path('admin/orders/<int:id>/update/', AdminOrderUpdateView.as_view(), name='admin_order_update'),
    # Admin Dashboard
    path("dashboard/", DashboardStatsView.as_view(), name="dashboard_stats"),
    path(
        "dashboard/user/<int:user_id>/",
        DashboardProductListView.as_view(),
        name="dashboard_products",
    ), 
    path(
        "dashboard/create-product/",
        DashboardProductCreateApi.as_view(),
        name="create_product",
    ),
    path(
        "dashboard/update-product/<int:id>/",
        DashboardProductUpdateApi.as_view(),
        name="update_product",
    ),
    path(
        "dashboard/product/<int:id>/delete/",
        DashboardProductDeleteApi.as_view(),
        name="delete_product",
    ),
    # Contact
    path("contact/", contact_email, name="contact_email"),
    path('send-order-email/', send_order_email, name='send_order_email'),
]
