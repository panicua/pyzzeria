from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from pizza_delivery.models import Customer, Order, DishOrder, Dish


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "phone_number",
        "status",
        "created_at",
    )
    list_display_links = (
        "id",
        "email",
    )
    list_editable = ("status",)
    list_filter = ("status",)
    search_fields = (
        "id",
        "email",
        "phone_number",
        "status",
    )


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "price",
        "weight",
    )
    list_display_links = (
        "id",
        "name",
    )
    list_editable = (
        "price",
        "weight",
    )
    list_filter = (
        "price",
        "price",
        "weight",
    )
    search_fields = (
        "id",
        "name",
    )


@admin.register(DishOrder)
class DishOrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "dish",
        "dish_amount",
    )
    list_display_links = (
        "id",
        "dish",
        "order",
    )
    list_editable = ("dish_amount",)
    list_filter = ("order",)
    search_fields = (
        "id",
        "dish",
        "order",
    )


@admin.register(Customer)
class CustomerAdmin(UserAdmin):
    list_display = UserAdmin.list_display + (
        "id",
        "phone_number",
    )
    list_display_links = (
        "id",
        "username",
    )
    list_filter = (
        "is_staff",
        "username",
    )
    search_fields = (
        "id",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "username",
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Additional info",
            {
                "fields": (
                    "email",
                    "phone_number",
                    "address",
                )
            },
        ),
    )
    fieldsets = UserAdmin.fieldsets + (
        (
            "Additional info",
            {
                "fields": (
                    "phone_number",
                    "address",
                )
            },
        ),
    )
