from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.http import HttpResponse
from django.urls import reverse
from phonenumber_field.modelfields import PhoneNumberField


class Ingredient(models.Model):
    name = models.CharField(max_length=64, db_index=True)

    class Meta:
        verbose_name = "ingredient"
        verbose_name_plural = "ingredients"

    def __str__(self):
        return self.name


class Dish(models.Model):
    name = models.CharField(max_length=64, db_index=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    weight = models.PositiveIntegerField()
    ingredients = models.ManyToManyField(
        Ingredient, through="DishIngredient", related_name="dishes", blank=True
    )
    image = models.URLField(null=True, blank=True)

    class Meta:
        verbose_name = "dish"
        verbose_name_plural = "dishes"

    def get_absolute_url(self) -> HttpResponse:
        return reverse("pizza_delivery:dish-detail", kwargs={"pk": self.pk})

    def __str__(self):
        return f"{self.name} (price: {self.price}, weight: {self.weight})"


class DishIngredient(models.Model):
    dish = models.ForeignKey(
        Dish, on_delete=models.CASCADE, related_name="dish_ingredients"
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name="ingredient_dishes"
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("dish", "ingredient")


class Order(models.Model):
    STATUS_CHOICES = (
        ("created", "Created"),
        ("approved", "Approved"),
        ("canceled", "Canceled"),
        ("delivered", "Delivered"),
    )
    dish = models.ManyToManyField(
        Dish, related_name="orders", blank=True, through="DishOrder"
    )
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    asked_date_delivery = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=64, blank=True, null=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    email = models.EmailField(max_length=64, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    customer = models.ForeignKey(
        "Customer",
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True,
    )
    session_key = models.CharField(
        max_length=32, null=True, blank=True, db_index=True
    )

    class Meta:
        ordering = ("-created_at",)

    @property
    def order_price(self) -> Decimal:
        total_price = Decimal("0.00")
        for order_dish in self.order_dishes.all():
            total_price += order_dish.dish.price * order_dish.dish_amount
        return total_price

    def __str__(self):
        return (
            f"Order status: {self.status}, "
            f"created_at: {self.created_at}, "
            f"updated_at: {self.updated_at}"
        )


class DishOrder(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_dishes"
    )
    dish = models.ForeignKey(
        Dish, on_delete=models.CASCADE, related_name="dish_orders"
    )
    dish_amount = models.IntegerField(default=1)


class Customer(AbstractUser):
    email = models.EmailField(max_length=64)
    phone_number = PhoneNumberField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    REQUIRED_FIELDS = [
        "email",
    ]

    class Meta:
        verbose_name = "customer"
        verbose_name_plural = "customers"

    def __str__(self):
        return f"{self.username} ({self.first_name} {self.last_name})"
