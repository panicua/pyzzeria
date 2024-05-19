from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from pizza_delivery.models import Customer, Order, DishOrder, Dish, Ingredient, \
    DishIngredient


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


class DishIngredientInline(admin.TabularInline):
    model = DishIngredient
    extra = 1


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
        "weight",
    )
    search_fields = (
        "id",
        "name",
        "ingredients__name",
    )
    inlines = [DishIngredientInline]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )
    list_display_links = (
        "id",
        "name",
    )
    list_filter = (
        "name",
    )
    search_fields = (
        "id",
        "name",
    )
