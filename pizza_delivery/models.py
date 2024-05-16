from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser
from decimal import Decimal
from phonenumber_field.modelfields import PhoneNumberField


class Dish(models.Model):
    name = models.CharField(max_length=64, db_index=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    weight = models.DecimalField(max_digits=8, decimal_places=2)
    ingredients = models.CharField(max_length=255)
    image = models.ImageField(upload_to='dishes/', null=True, blank=True)

    class Meta:
        verbose_name = "dish"
        verbose_name_plural = "dishes"

    def __str__(self):
        return f"{self.name} (price: {self.price}, weight: {self.weight})"


class Order(models.Model):
    STATUS_CHOICES = (
        ("created", "Created"),
        ("approved", "Approved"),
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
    asked_date_delivery = models.DateTimeField()
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))])
    phone_number = PhoneNumberField(blank=True, null=True)
    email = models.EmailField(unique=True, max_length=64)
    address = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ("-created_at", )

    def calculate_order_price(self):
        total_price = Decimal('0.00')
        for order_dish in self.order_dishes.all():
            total_price += order_dish.dish.price * order_dish.dish_amount
        self.price = total_price
        self.save()

    def __str__(self):
        return (
            f"Order status: {self.status}, "
            f"created_at: {self.created_at}, "
            f"total_price: {self.price}"
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
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        related_name="customer_order",
        null=True,
        blank=True,
    )
    email = models.EmailField(unique=True, max_length=64)
    phone_number = PhoneNumberField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    REQUIRED_FIELDS = ["email", ]

    class Meta:
        verbose_name = "customer"
        verbose_name_plural = "customers"

    def __str__(self):
        return f"{self.username} ({self.first_name} {self.last_name})"
