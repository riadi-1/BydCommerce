from django.urls import path, include
from buyedinn import views

app_name = "buyedinn"

urlpatterns = [
    # home
    path("", views.index, name="index"),
    path("sign-up/", views.register_view, name="sign-up"),
    path("sign-in/", views.login_view, name="sign-in"),
    path("sign-out/", views.logout_view, name="sign-out"),

    # product
    path("products/", views.product_list_view, name="product-list"),
    path("product/<pid>/", views.product_detail_view, name="product-detail"),

    # category
    path("category/", views.category_list_view, name="category-list"),
    path("category/<cid>/", views.category_product_list_view, name="category-product-list"),

    # vendor
    path("vendors/", views.vendor_list_view, name="vendor-list"),
    path("vendor/<vid>/", views.vendor_detail_view, name="vendor-detail"),

    # search
    path("search/", views.search_view, name="search"),

    # filter Product URL
    path("filter-products", views.filter_product, name="filter-product"),

    # add to cart URL
    path("add-to-cart/", views.add_to_cart, name="add-to-cart"),

    # Cart Page URL
    path("cart/", views.cart_view, name="cart"),

    # Delete Item from Cart
    path("delete-from-cart/", views.delete_item_from_cart, name="delete-from-cart"),

    # Update Item from Cart
    path("update-cart/", views.update_cart, name="update-cart"),

    # Checkout URL
    path("checkout/", views.checkout_view, name="checkout"),

    # Paypal Getway
    path('paypal/', include('paypal.standard.ipn.urls')),

    # payment successful
    path("payment-completed", views.payment_completed_view, name="payment-completed"),

    # payment failed
    path("payment-failed", views.payment_failed_view, name="payment-failed"),

    # Dashboard URL
    path("dashboard/", views.customer_dashboard, name="dashboard"),

    # Order Detail URL
    path("dashboard/order/<int:id>", views.order_detail, name="order-detail"),

    # Making address default
    path("make-default-address/", views.make_address_default, name="make-default-address"),

    # Making address default
    path("profile/update/", views.profile_update, name="profile-update")

]
