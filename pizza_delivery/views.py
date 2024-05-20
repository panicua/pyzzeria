from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest, HttpRequest, \
    HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from pizza_delivery.forms import (
    RegistrationForm,
    UserLoginForm,
    CustomerUpdateForm,
    DishSearchForm,
    UserPasswordChangeForm,
    OrderUpdateForm,
)
from pizza_delivery.models import Customer, Dish, Order, DishOrder
from pizza_delivery.utils import (
    get_user_orders,
    get_orders_for_customer_or_session,
)


def index(request) -> HttpResponse | HttpResponseBadRequest:
    if request.method == "POST":
        return HttpResponseBadRequest("Method not allowed")

    orders_info = get_user_orders(request)

    query = request.GET.get("query", "")
    sort_order = request.GET.get("sort", "asc")

    dishes = Dish.objects.prefetch_related("dish_orders").order_by("name")

    if query:
        dishes = dishes.filter(
            Q(name__icontains=query) | Q(ingredients__name__icontains=query)
        ).distinct()

    if sort_order == "asc":
        dishes = dishes.order_by("price")
    elif sort_order == "desc":
        dishes = dishes.order_by("-price")

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
        "search_form": DishSearchForm(initial={"query": query}),
        "sort_order": sort_order,
        "order_list": orders_info["order_items"],
        "total_price": orders_info["total_price"],
    }

    return render(request, "pages/index.html", context=context)


def add_remove_dish_button(request) -> (
        HttpResponse | HttpResponseBadRequest
):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method")

    try:
        new_dish = Dish.objects.get(pk=request.POST.get("dish_id"))
    except Dish.DoesNotExist:
        return HttpResponseBadRequest("Dish does not exist")

    customer = request.user
    session_key = request.session.session_key

    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    action = request.POST.get("action")
    created_order_list = get_orders_for_customer_or_session(request)

    if action == "add_one":
        dish_added = False

        for order in created_order_list:
            try:
                dish_order = DishOrder.objects.get(order=order, dish=new_dish)
                dish_order.dish_amount += 1
                dish_order.save()
                dish_added = True
                return HttpResponse(
                    "Dish added to an existing order successfully", status=200
                )
            except DishOrder.DoesNotExist:
                continue

        if not dish_added:
            order = Order.objects.create(
                status="created",
                customer=customer if customer.is_authenticated else None,
                session_key=(
                    session_key if not customer.is_authenticated else None
                ),
                asked_date_delivery=timezone.now(),
                name="",
                phone_number="",
                email="",
                address="",
            )
            DishOrder.objects.create(order=order, dish=new_dish, dish_amount=1)
            return HttpResponse(
                "Dish added to a new order successfully", status=201
            )

    elif action == "remove_one":
        for order in created_order_list:
            try:
                dish_order = DishOrder.objects.get(order=order, dish=new_dish)
                if dish_order.dish_amount > 1:
                    dish_order.dish_amount -= 1
                    dish_order.save()
                    return HttpResponse(
                        "One dish removed from an existing order successfully",
                        status=200,
                    )
                else:
                    dish_order.delete()
                    if not DishOrder.objects.filter(order=order).exists():
                        order.delete()
                    return HttpResponse(
                        "Dish completely removed from "
                        "an existing order successfully",
                        status=200,
                    )
            except DishOrder.DoesNotExist:
                continue

    return HttpResponseBadRequest("Invalid action")


def order_complete(request: HttpRequest) -> (
        HttpResponse | HttpResponseRedirect
):
    orders_info = get_user_orders(request)
    customer = request.user

    orders = get_orders_for_customer_or_session(request)

    if request.method == "POST":
        form = OrderUpdateForm(request.POST, customer=customer)
        if form.is_valid():
            for order in orders:
                for field, value in form.cleaned_data.items():
                    setattr(order, field, value)
                order.status = "approved"
                order.save()
            messages.success(
                request,
                "Order approved successfully."
                "Operator will contact you soon.",
            )
            return redirect("pizza_delivery:index")
    elif not orders:
        return redirect("pizza_delivery:index")
    else:
        form = OrderUpdateForm(customer=customer)

    context = {
        "form": form,
        "order_list": orders_info["order_items"],
        "total_price": orders_info["total_price"],
    }

    return render(request, "pages/order_complete.html", context=context)


def clean_order(request: HttpRequest) -> HttpResponseRedirect:
    orders = get_orders_for_customer_or_session(request)
    for order in orders:
        order.delete()
    return redirect("pizza_delivery:index")


class DishDetailView(generic.DetailView):
    model = Dish
    queryset = Dish.objects.prefetch_related("orders")
    template_name = "pages/dish_detail.html"


class CustomerUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Customer
    form_class = CustomerUpdateForm
    template_name = f"pages/customer_profile.html"

    def get_object(self, queryset=None) -> Customer:
        customer = super().get_object(queryset)
        if customer != self.request.user:
            raise PermissionDenied("You can only edit your own profile.")
        return customer

    def get_success_url(self) -> HttpResponseRedirect:
        messages.success(self.request, "Profile updated successfully.")
        return reverse(
            "pizza_delivery:profile", kwargs={"pk": self.object.pk or None}
        )


def about_us(request: HttpRequest) -> HttpResponse:
    return render(request, "pages/about-us.html")


def contact_us(request: HttpRequest) -> HttpResponse:
    return render(request, "pages/contact-us.html")


# Authentication
def register(request: HttpRequest) -> HttpResponse | HttpResponseRedirect:
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            print("Account created successfully!")
            return redirect("/accounts/login")
        else:
            print("Registration failed!")
    else:
        form = RegistrationForm()

    context = {"form": form}
    return render(request, "accounts/sign-up.html", context)


class UserLoginView(LoginView):
    template_name = "accounts/sign-in.html"
    form_class = UserLoginForm


def logout_view(request) -> HttpResponseRedirect:
    logout(request)
    return redirect("pizza_delivery:login")


class UserPasswordChangeView(PasswordChangeView):
    template_name = "accounts/password_change.html"
    form_class = UserPasswordChangeForm

    def get_success_url(self) -> HttpResponseRedirect:
        logout(self.request)
        messages.success(self.request, "Password changed successfully.")
        return reverse("pizza_delivery:login")
