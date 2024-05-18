from django.urls import path
from pizza_delivery.views import (
    index, presentation, page_header, features,
    navbars, nav_tabs, pagination, inputs,
    forms, alerts, modals, tooltips,
    avatars, badges, breadcrumbs, buttons,
    dropdowns, progress_bars, toggles, typography,
    about_us, contact_us, author, UserLoginView,
    register, logout_view, UserPasswordChangeView,
    UserPasswordResetView, UserPasswordResetConfirmView, DishDetailView,
    add_remove_dish_button, order_complete, clean_order
)

from django.contrib.auth import views as auth_views

urlpatterns = [
    # Main Logic
    path("", index, name="index"),
    path(
        "dishes/<int:pk>/", DishDetailView.as_view(), name="dish-detail"
    ),
    path("order/add_remove_dish", add_remove_dish_button, name="add-remove-dish-button"),
    path("order/clean", clean_order, name="clean-order"),
    path('order_complete/', order_complete, name='order-complete'),

    # Top Bar
    path('about-us/', about_us, name='about-us'),
    path('contact-us/', contact_us, name='contact-us'),
    path('author/', author, name='author'),

# Authentication
    path('accounts/login/', UserLoginView.as_view(), name='login'),
    path('accounts/register/', register, name='register'),
    path('accounts/logout/', logout_view, name='logout'),
    path('accounts/password-change/', UserPasswordChangeView.as_view(), name='password_change'),
    path('accounts/password-change-done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'
    ), name='password_change_done'),
    path('accounts/password-reset/', UserPasswordResetView.as_view(), name='password_reset'),
    path('accounts/password-reset-done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('accounts/password-reset-confirm/<uidb64>/<token>/',
        UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),

    # Sections
    path('presentation/', presentation, name='presentation'),
    path('page-header/', page_header, name='page_header'),
    path('features/', features, name='features'),
    path('navbars/', navbars, name='navbars'),
    path('nav-tabs/', nav_tabs, name='nav_tabs'),
    path('pagination/', pagination, name='pagination'),
    path('inputs/', inputs, name='inputs'),
    path('forms/', forms, name='forms'),
    path('alerts/', alerts, name='alerts'),
    path('modals/', modals, name='modals'),
    path('tooltips/', tooltips, name='tooltips'),
    path('avatars/', avatars, name='avatars'),
    path('badges/', badges, name='badges'),
    path('breadcrumbs/', breadcrumbs, name='breadcrumbs'),
    path('buttons/', buttons, name='buttons'),
    path('dropdowns/', dropdowns, name='dropdowns'),
    path('progress-bars/', progress_bars, name='progress_bars'),
    path('toggles/', toggles, name='toggles'),
    path('typography/', typography, name='typography'),

]


app_name = "pizza_delivery"
