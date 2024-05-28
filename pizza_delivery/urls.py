from django.urls import path

from pizza_delivery.views import (
    index,
    about_us,
    contact_us,
    UserLoginView,
    register,
    logout_view,
    DishDetailView,
    add_remove_dish_button,
    order_complete,
    clean_order,
    CustomerUpdateView,
    UserPasswordChangeView,
)

urlpatterns = [
    # Main Logic
    path("", index, name="index"),
    path("profile/<int:pk>/", CustomerUpdateView.as_view(), name="profile"),
    path("dishes/<int:pk>/", DishDetailView.as_view(), name="dish-detail"),
    path(
        "order/add_remove_dish/",
        add_remove_dish_button,
        name="add-remove-dish-button",
    ),
    path("order/clean/", clean_order, name="clean-order"),
    path("order_complete/", order_complete, name="order-complete"),
    # Top Bar
    path("about-us/", about_us, name="about-us"),
    path("contact-us/", contact_us, name="contact-us"),
    # Authentication
    path("accounts/login/", UserLoginView.as_view(), name="login"),
    path("accounts/register/", register, name="register"),
    path("accounts/logout/", logout_view, name="logout"),
    path(
        "accounts/password_change/",
        UserPasswordChangeView.as_view(),
        name="password-change",
    ),
]

app_name = "pizza_delivery"
