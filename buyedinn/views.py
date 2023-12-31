import calendar

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import ExtractMonth
from django.http import JsonResponse
from django.shortcuts import render, redirect
from buyedinn.forms import UserRegisterForm, ProfileForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings
from django.template.loader import render_to_string

from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from django.contrib.auth.decorators import login_required
from buyedinn.models import (Product, Category, Vendor, CartOrder, CartOrderItems, ProductReview,
                             ProductImages,
                             Address, Wishlist, Profile, Tags)

User = settings.AUTH_USER_MODEL


# it shows the landing page
def index(request):
    # products = Product.objects.all().order_by("-id")
    products = Product.objects.filter(product_status="published", featured=True)

    context = {
        "products": products
    }
    return render(request, 'core/index.html', context)


# for user registration
def register_view(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST or None)
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f'Hey {username}, You account was created successfully')
            new_user = authenticate(username=form.cleaned_data['email'],
                                    password=form.cleaned_data['password1']
                                    )
            login(request, new_user)
            return redirect("buyedinn:index")

    else:
        form = UserRegisterForm()

    context = {
        'form': form,
    }
    return render(request, "userauths/sign-up.html", context)


# for user login
def login_view(request):
    if request.user.is_authenticated:
        messages.warning(request, f"Hey you are already Logged In")
        return redirect("buyedinn:index")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
        except:
            messages.warning(request, f"User with{email} does not exist")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "You are logged in.")
            return redirect("buyedinn:index")
        else:
            messages.warning(request, "User Does Not Exist. Create an account")
    context = {
    }
    return render(request, "userauths/sign-in.html", context)


# for user logout
def logout_view(request):
    logout(request)
    messages.success(request, "You logged out.")
    return redirect("buyedinn:sign-in")


# for listing products
def product_list_view(request):
    products = Product.objects.filter(product_status="published")
    categories = Category.objects.all()
    vendors = Vendor.objects.all()

    context = {
        "products": products,
        "categories": categories,
        "vendors": vendors,
    }
    return render(request, 'core/product-list.html', context)


# for listing product by categories
def category_list_view(request):
    categories = Category.objects.all()

    context = {
        "categories": categories,

    }
    return render(request, 'core/category-list.html', context)


def category_product_list_view(request, cid):
    category = Category.objects.get(cid=cid)
    products = Product.objects.filter(product_status="published", category=category)

    context = {
        "category": category,
        "products": products,

    }
    return render(request, "core/category-product-list.html", context)


def vendor_list_view(request):
    vendors = Vendor.objects.all()
    context = {
        "vendors": vendors,
    }
    return render(request, "core/vendor-list.html", context)


def vendor_detail_view(request, vid):
    vendor = Vendor.objects.get(vid=vid)
    products = Product.objects.filter(vendor=vendor, product_status="published")
    categories = Category.objects.all()

    context = {
        "vendor": vendor,
        "products": products,
        "categories": categories

    }
    return render(request, "core/vendor-detail.html", context)


def product_detail_view(request, pid):
    product = Product.objects.get(pid=pid)
    p_image = product.p_images.all()
    address = Address.objects.filter(user=request.user)
    products = Product.objects.filter(category=product.category).exclude(pid=pid)

    context = {
        "products": product,
        "p_image": p_image,
        "address": address,
        "p": products,

    }
    return render(request, "core/product-detail.html", context)

def search_view(request):
    query = request.GET.get("q")

    products = Product.objects.filter(title__icontains=query).order_by("-date")

    context = {
        "products": products,
        "query": query,
    }
    return render(request, "core/search.html", context)


def filter_product(request):
    categories = request.GET.getlist("category[]")
    vendors = request.GET.getlist("vendor[]")

    products = Product.objects.filter(product_status="published").order_by("-id").distinct()

    if len(categories) > 0:
        products = products.filter(category__id__in=categories).distinct()

    if len(vendors) > 0:
        products = products.filter(vendor__id__in=vendors).distinct()

    data = render_to_string("core/async/product-list.html", {"products": products})
    return JsonResponse({"data": data})

def add_to_cart(request):
    cart_product = {}

    cart_product[str(request.GET['id'])] = {
        'title': request.GET['title'],
        'qty': request.GET['qty'],
        'price': request.GET['price'],
        'image': request.GET['image'],
        'pid': request.GET['pid'],

    }

    if 'cart_data_obj' in request.session:
        if str(request.GET['id']) in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            cart_data[str(request.GET['id'])]['qty'] = int(cart_product[str(request.GET['id'])]['qty'])
            cart_data.update(cart_data)
            request.session['cart_data_obj'] = cart_data
        else:
            cart_data = request.session['cart_data_obj']
            cart_data.update(cart_product)
            request.session['cart_data_obj'] = cart_data
    else:
        request.session['cart_data_obj'] = cart_product
    return JsonResponse(
        {"data": request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj'])})


def cart_view(request):
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
        return render(request, "core/cart.html", {"cart_data": request.session['cart_data_obj'],
                                                  'totalcartitems': len(request.session['cart_data_obj']),
                                                  'cart_total_amount': cart_total_amount})
    else:
        return render(request, "core/cart.html", {"cart_data": '',
                                                  'totalcartitems': len(request.session['cart_data_obj']),
                                                  'cart_total_amount': cart_total_amount})

    return render(request, "core/cart.html")


def delete_item_from_cart(request):
    product_id = str(request.GET['id'])
    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            del request.session['cart_data_obj'][product_id]
            request.session['cart_data_obj'] = cart_data
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

    context = render_to_string("core/async/cart-list.html", {"cart_data": request.session['cart_data_obj'],
                                                             'totalcartitems': len(request.session['cart_data_obj']),
                                                             'cart_total_amount': cart_total_amount})
    return JsonResponse({"data": context, 'totalcartitems': len(request.session['cart_data_obj'])})


def update_cart(request):
    product_id = str(request.GET['id'])
    product_qty = request.GET['qty']

    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            cart_data[str(request.GET['id'])]['qty'] = product_qty
            request.session['cart_data_obj'] = cart_data

    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

    context = render_to_string("core/async/cart-list.html", {"cart_data": request.session['cart_data_obj'],
                                                             'totalcartitems': len(request.session['cart_data_obj']),
                                                             'cart_total_amount': cart_total_amount})
    return JsonResponse({"data": context, 'totalcartitems': len(request.session['cart_data_obj'])})


@login_required
def checkout_view(request):
    cart_total_amount = 0
    total_amount = 0

    # checking if cart_data_obj session exist
    if 'cart_data_obj' in request.session:
        # Getting total amount for Paypal Amount
        for p_id, item in request.session['cart_data_obj'].items():
            total_amount += int(item['qty']) * float(item['price'])

        # create Order Object
        order = CartOrder.objects.create(
            user=request.user,
            price=total_amount
        )

        # getting total amount for the cart
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

            cart_order_products = CartOrderItems.objects.create(
                order=order,
                invoice_no="INVOICE_NO" + str(order.id),
                item=item['title'],
                image=item['image'],
                qty=item['qty'],
                price=item['price'],
                total=float(item['qty']) * float(item['price'])

            )

    host = request.get_host()
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': cart_total_amount,
        'item_name': "Order-Item-No-" + str(order.id),
        'invoice': "INVOICE_NO-" + str(order.id),
        'currency_code': "USD",
        'notify_url': 'http://{}{}'.format(host, reverse("buyedinn:paypal-ipn")),
        'return_url': 'http://{}{}'.format(host, reverse("buyedinn:payment-completed")),
        'cancel_url': 'http://{}{}'.format(host, reverse("buyedinn:payment-failed")),
    }

    paypal_payment_button = PayPalPaymentsForm(initial=paypal_dict)

    try:
        active_address = Address.objects.get(user=request.user, status=True)

    except:
        messages.warning(request, "There are multiple addresses, only one should be activated.")
        active_address = None

    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

        return render(request, "core/checkout.html", {"cart_data": request.session['cart_data_obj'],
                                                      'totalcartitems': len(request.session['cart_data_obj']),
                                                      'cart_total_amount': cart_total_amount,
                                                      'paypal_payment_button': paypal_payment_button,
                                                      "active_address": active_address})


@login_required
def payment_completed_view(request):
    cart_total_amount = 0
    for product_id, item in request.session['cart_data_obj'].items():
        cart_total_amount += int(item['qty']) * float(item['price'])
    context = request.POST
    return render(request, 'core/payment-completed.html', {"cart_data": request.session['cart_data_obj'],
                                                           'totalcartitems': len(request.session['cart_data_obj']),
                                                           'cart_total_amount': cart_total_amount})


@login_required
def payment_failed_view(request):
    return render(request, 'core/payment-failed.html')

#BADR ###########################################################333
@login_required
def customer_dashboard(request):
    orders = CartOrder.objects.filter(user=request.user).order_by("-id")
    address = Address.objects.filter(user=request.user)

    profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        address = request.POST.get("address")
        mobile = request.POST.get("mobile")

        new_address = Address.objects.create(
            user=request.user,
            address=address,
            mobile=mobile,
        )
        messages.success(request, "Address Added Seccessfully.")
        return redirect("buyedinn:dashboard")

    context = {
        "profile": profile,
        "orders": orders,
        "address": address,
    }
    return render(request, 'core/dashboard.html', context)


def order_detail(request, id):
    order = CartOrder.objects.get(user=request.user, id=id)
    order_items = CartOrderItems.objects.filter(order=order)
    context = {
        "order_items": order_items,
    }
    return render(request, 'core/order-detail.html', context)


def make_address_default(request):
    id = request.GET['id']
    Address.objects.update(status=False)
    Address.objects.filter(id=id).update(status=True)
    return JsonResponse({"boolean": True})


def profile_update(request):
    profile = Profile.objects.get(user=request.user)
    form = ProfileForm(instance=profile)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.user = request.user
            new_form.save()
            messages.success(request, "Profile Updated Successfully!")
            return redirect("buyedinn:dashboard")
        else:
            form = ProfileForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, "userauths/profile-edit.html", context)

# def profile_update(request):
#     form = ProfileForm()
#
#     context = {
#         "form": form,
#     }
#     return render(request, "userauths/profile-edit.html")
