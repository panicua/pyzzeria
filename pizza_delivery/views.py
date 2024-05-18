from datetime import timedelta
from decimal import Decimal

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, PasswordResetView, \
    PasswordChangeView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.views import generic

from pizza_delivery.forms import RegistrationForm, UserLoginForm, \
    UserPasswordResetForm, UserSetPasswordForm, UserPasswordChangeForm, \
    DishSearchForm, OrderUpdateForm
from django.contrib.auth import logout

from pizza_delivery.models import Dish, Order, DishOrder

from django.utils import timezone


# Pages
def index(request):
    orders_info = get_user_orders(request)

    name = request.GET.get("name", "")
    sort_order = request.GET.get("sort", "asc")

    dishes = Dish.objects.prefetch_related("dish_orders").order_by("name")

    # Search
    if name:
        dishes = dishes.filter(name__icontains=name)

    # Sort
    if sort_order == "asc":
        dishes = dishes.order_by("price")
    elif sort_order == "desc":
        dishes = dishes.order_by("-price")

    # Paginator
    paginator = Paginator(dishes, 6)
    page_number = request.GET.get("page")

    try:
        dishes = paginator.page(page_number)
    except PageNotAnInteger:
        dishes = paginator.page(1)
    except EmptyPage:
        dishes = paginator.page(paginator.num_pages)

    context = {
        "dishes_list": dishes,
        "page_obj": dishes,
        "search_form": DishSearchForm(initial={"name": name}),
        "sort_order": sort_order,
        "order_list": orders_info["order_items"],
        "total_price": orders_info["total_price"]
    }

    return render(request, 'pages/index.html', context=context)


def get_user_orders(request):
    session_key = request.session.session_key
    customer = request.user

    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    if customer.is_authenticated:
        orders = Order.objects.filter(customer=customer, status="created")
    else:
        orders = Order.objects.filter(session_key=session_key, status="created")

    order_items = []
    total_price = Decimal('0.00')
    for order in orders:
        dish_orders = DishOrder.objects.filter(order=order)
        for dish_order in dish_orders:
            total_price += dish_order.dish.price * dish_order.dish_amount
            order_items.append({
                'dish_name': dish_order.dish.name,
                'dish_amount': dish_order.dish_amount,
            })

    return {
        'order_items': order_items,
        'total_price': total_price
    }


def add_remove_dish_button(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid request method')

    try:
        new_dish = Dish.objects.get(pk=request.POST.get('dish_id'))
    except Dish.DoesNotExist:
        return HttpResponseBadRequest('Dish does not exist')

    customer = request.user
    session_key = request.session.session_key

    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    if request.POST.get('action') == 'add_one':
        if customer.is_authenticated:
            created_order_list = Order.objects.filter(
                customer=customer,
                status="created"
            )
        else:
            created_order_list = Order.objects.filter(
                session_key=session_key,
                status="created"
            )

        for order in created_order_list:
            try:
                dish_order = DishOrder.objects.get(order=order, dish=new_dish)
                dish_order.dish_amount += 1
                dish_order.save()
                return HttpResponse('Dish added to an existing order successfully', status=200)
            except DishOrder.DoesNotExist:
                HttpResponseBadRequest('Dish doesnt exist in the order')

        # Create a new order if no existing order matches
        date_to_pass = timezone.now()
        order = Order.objects.create(
            status="created",
            customer=customer if customer.is_authenticated else None,
            session_key=session_key if not customer.is_authenticated else None,
            asked_date_delivery=date_to_pass,
            name="",
            phone_number="",
            email="",
            address="",
        )
        DishOrder.objects.create(order=order, dish=new_dish, dish_amount=1)
        return HttpResponse('Dish added to a new order successfully', status=201)

    elif request.POST.get('action') == 'remove_one':
        if customer.is_authenticated:
            created_order_list = Order.objects.filter(
                customer=customer,
                status="created"
            )
        else:
            created_order_list = Order.objects.filter(
                session_key=session_key,
                status="created"
            )
        for order in created_order_list:
            try:
                dish_order = DishOrder.objects.get(order=order, dish=new_dish)
                if dish_order.dish_amount > 1:
                    dish_order.dish_amount -= 1
                    dish_order.save()
                    return HttpResponse(
                        'One dish removed from an existing order successfully',
                        status=200)
                else:
                    dish_order.order.delete()
                    return HttpResponse(
                        'Dish completely removed from an existing order successfully',
                        status=200)
            except DishOrder.DoesNotExist:
                HttpResponseBadRequest('Dish doesnt exist in the order')

    return HttpResponseBadRequest('Invalid action')


def order_complete(request):
    customer = request.user
    session_key = request.session.session_key
    orders_info = get_user_orders(request)

    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    if customer.is_authenticated:
        orders = Order.objects.filter(customer=customer, status="created")
    else:
        orders = Order.objects.filter(session_key=session_key, status="created")

    if request.method == 'POST':
        form = OrderUpdateForm(request.POST)
        if form.is_valid():
            for order in orders:
                for field, value in form.cleaned_data.items():
                    setattr(order, field, value)
                order.status = 'approved'
                order.save()
            return redirect('pizza_delivery:index')
    elif not orders:
        return redirect('pizza_delivery:index')
    else:
        form = OrderUpdateForm()

    context = {
        'form': form,
        "order_list": orders_info["order_items"],
        "total_price": orders_info["total_price"],
    }

    return render(request, 'pages/order_complete.html', context=context)


class DishDetailView(generic.DetailView):
    model = Dish
    queryset = Dish.objects.prefetch_related("orders")
    template_name = "pages/dish_detail.html"


def about_us(request):
    return render(request, 'pages/about-us.html')


def contact_us(request):
    return render(request, 'pages/contact-us.html')


def author(request):
    return render(request, 'pages/author.html')


# Authentication

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            print("Account created successfully!")
            return redirect('/accounts/login')
        else:
            print("Registration failed!")
    else:
        form = RegistrationForm()

    context = {'form': form}
    return render(request, 'accounts/sign-up.html', context)


class UserLoginView(LoginView):
    template_name = 'accounts/sign-in.html'
    form_class = UserLoginForm


def logout_view(request):
    logout(request)
    return redirect('/accounts/login')


class UserPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    form_class = UserPasswordResetForm


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    form_class = UserSetPasswordForm


class UserPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = UserPasswordChangeForm


# Sections
def presentation(request):
    return render(request, 'sections/presentation.html')


def page_header(request):
    return render(request, 'sections/page-sections/hero-sections.html')


def features(request):
    return render(request, 'sections/page-sections/features.html')


def navbars(request):
    return render(request, 'sections/navigation/navbars.html')


def nav_tabs(request):
    return render(request, 'sections/navigation/nav-tabs.html')


def pagination(request):
    return render(request, 'sections/navigation/pagination.html')


def inputs(request):
    return render(request, 'sections/input-areas/inputs.html')


def forms(request):
    return render(request, 'sections/input-areas/forms.html')


def avatars(request):
    return render(request, 'sections/elements/avatars.html')


def badges(request):
    return render(request, 'sections/elements/badges.html')


def breadcrumbs(request):
    return render(request, 'sections/elements/breadcrumbs.html')


def buttons(request):
    return render(request, 'sections/elements/buttons.html')


def dropdowns(request):
    return render(request, 'sections/elements/dropdowns.html')


def progress_bars(request):
    return render(request, 'sections/elements/progress-bars.html')


def toggles(request):
    return render(request, 'sections/elements/toggles.html')


def typography(request):
    return render(request, 'sections/elements/typography.html')


def alerts(request):
    return render(request, 'sections/attention-catchers/alerts.html')


def modals(request):
    return render(request, 'sections/attention-catchers/modals.html')


def tooltips(request):
    return render(request,
                  'sections/attention-catchers/tooltips-popovers.html')
