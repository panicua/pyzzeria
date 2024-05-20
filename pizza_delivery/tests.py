from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from pizza_delivery.models import Dish, Order, DishOrder, Ingredient, \
    DishIngredient


class PizzaDeliveryTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="testuser", password="12345"
        )
        self.dish = Dish.objects.create(
            name="Test Pizza",
            price=10.0,
            description="Test description",
            weight=500,
        )
        self.index_url = reverse("pizza_delivery:index")
        self.add_remove_dish_url = reverse(
            "pizza_delivery:add-remove-dish-button"
        )
        self.order_complete_url = reverse("pizza_delivery:order-complete")
        self.profile_url = reverse(
            "pizza_delivery:profile", kwargs={"pk": self.user.id}
        )

    def test_index_view_get(self):
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/index.html")
        self.assertContains(response, "Test Pizza")

    def test_index_view_post_invalid(self):
        response = self.client.post(self.index_url, {})
        self.assertEqual(response.status_code, 400)

    def test_add_dish_button_post(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.post(
            self.add_remove_dish_url,
            {"action": "add_one", "dish_id": self.dish.id}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(DishOrder.objects.count(), 1)
        self.assertEqual(DishOrder.objects.first().dish_amount, 1)

    def test_remove_dish_button_twice_post(self):
        self.client.login(username="testuser", password="12345")
        self.client.post(
            self.add_remove_dish_url,
            {"action": "add_one", "dish_id": self.dish.id}
        )
        response = self.client.post(
            self.add_remove_dish_url,
            {"action": "remove_one", "dish_id": self.dish.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(DishOrder.objects.count(), 0)

        new_response = self.client.post(
            self.add_remove_dish_url,
            {"action": "remove_one", "dish_id": self.dish.id}
        )
        self.assertEqual(new_response.status_code, 400)

    def test_order_complete_view_get(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(self.order_complete_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("pizza_delivery:index"))

    def test_order_complete_view_post_valid(self):
        self.client.login(username="testuser", password="12345")
        self.client.post(
            self.add_remove_dish_url,
            {"action": "add_one", "dish_id": self.dish.id}
        )
        response = self.client.post(
            self.order_complete_url,
            {
                "name": "John Doe",
                "phone_number": "+12125552368",
                "email": "john.doe@example.com",
                "address": "123 Streetasd",
                "asked_date_delivery": (
                    timezone.now() + timezone.timedelta(hours=3, minutes=40)
                ).strftime("%Y-%m-%dT%H:%M"),
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.first().status, "approved")
        self.assertEqual(Order.objects.count(), 1)

    def test_order_complete_view_post_invalid_time(self):
        self.client.login(username="testuser", password="12345")
        self.client.post(
            self.add_remove_dish_url,
            {"action": "add_one", "dish_id": self.dish.id}
        )
        response = self.client.post(
            self.order_complete_url,
            {
                "name": "John Doe",
                "phone_number": "phonenumber",
                "email": "john.doe@example.com",
                "address": "123 Streetasd",
                "asked_date_delivery": (
                    timezone.now() + timezone.timedelta(hours=3, minutes=40)
                ).strftime("%Y-%m-%dT%H:%M"),
            },
        )
        self.assertEqual(
            response.status_code, 200
        )  # Form error should return to the same page
        self.assertFormError(
            response,
            "form",
            "phone_number",
            "Enter a valid phone number (e.g. +12125552368).",
        )


class ProfilePageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="12345",
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone_number="+123456789",
            address="123 Street",
        )
        self.profile_url = reverse(
            "pizza_delivery:profile", kwargs={"pk": self.user.pk}
        )
        self.client.login(username="testuser", password="12345")

    def test_profile_view_get(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/customer_profile.html")
        self.assertContains(response, "John")

    def test_profile_view_post_valid(self):
        response = self.client.post(
            self.profile_url,
            {
                "first_name": "Johnny",
                "last_name": "Depp",
                "phone_number": "+987654321111",
                "email": "johnny@example.com",
                "address": "321 Streetasd",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Johnny")
        self.assertEqual(self.user.last_name, "Depp")
        self.assertEqual(self.user.phone_number, "+987654321111")
        self.assertEqual(self.user.email, "johnny@example.com")
        self.assertEqual(self.user.address, "321 Streetasd")

    def test_profile_view_post_invalid(self):
        response = self.client.post(
            self.profile_url,
            {
                "first_name": "Johnny",
                "last_name": "D",
                "phone_number": "invalid_phone_number",
                "email": "johnny@example.com",
                "address": "321 Street",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response,
            "form",
            "phone_number",
            "Enter a valid phone number (e.g. +12125552368).",
        )
        self.assertFormError(
            response,
            "form",
            "last_name",
            "Name must be at least 2 characters long"
        )
        self.assertFormError(
            response,
            "form",
            "address",
            "Address must contain at least 8 letters"
        )

    def test_access_to_profile_page_without_login(self):
        self.client.logout()
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, "/accounts/login/?next=" + self.profile_url
        )

    def test_access_to_other_users_profile_page(self):
        other_user = get_user_model().objects.create_user(
            username="otheruser",
            password="12345",
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone_number="+123456789",
            address="123 Street",
        )
        other_profile_url = reverse(
            "pizza_delivery:profile", kwargs={"pk": other_user.pk}
        )
        response = self.client.get(other_profile_url)
        self.assertEqual(response.status_code, 403)


class IndexSearchTests(TestCase):
    def setUp(self):
        self.dish = Dish.objects.create(
            name="Test Pizza",
            price=10.0,
            description="Test description",
            weight=500
        )
        self.index_url = reverse("pizza_delivery:index")

    def test_index_search_functionality(self):
        Dish.objects.create(
            name="Another Pizza",
            price=15.0,
            description="Another description",
            weight=500,
        )

        response = self.client.get(self.index_url, {"query": "Test"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Pizza")
        self.assertNotContains(response, "Another Pizza")

    def test_index_search_functionality_no_results(self):
        response = self.client.get(self.index_url, {"query": "Nonexistent"})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Test Pizza")

    def test_index_search_by_ingredient(self):
        mozzarella = Ingredient.objects.create(name="Mozzarella")
        pizza = Dish.objects.create(
            name="Another Pizza",
            price=15.0,
            description="Another description",
            weight=500,
        )
        DishIngredient.objects.create(
            dish=pizza, ingredient=mozzarella, quantity=1
        )

        response = self.client.get(self.index_url, {"query": "rella"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Another Pizza")
        self.assertNotContains(response, "Test Pizza")
