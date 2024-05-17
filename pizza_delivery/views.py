from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, PasswordResetView, \
    PasswordChangeView, PasswordResetConfirmView
from django.views import generic

from pizza_delivery.forms import RegistrationForm, UserLoginForm, \
    UserPasswordResetForm, UserSetPasswordForm, UserPasswordChangeForm, \
    DishSearchForm
from django.contrib.auth import logout

from pizza_delivery.models import Dish


# Create your views here.


# Pages
def index(request):
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
    }

    return render(request, 'pages/index.html', context=context)


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

