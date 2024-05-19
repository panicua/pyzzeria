from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, \
    PasswordResetForm, SetPasswordForm, PasswordChangeForm, UsernameField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from pizza_delivery.models import Dish, Order
from pizza_delivery.validators import customer_name_validator, \
    customer_phone_number_validator, customer_address_validator


class RegistrationForm(UserCreationForm):
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={'class': 'form-control form-control-lg',
                   'placeholder': 'Password'}),
    )
    password2 = forms.CharField(
        label=_("Password Confirmation"),
        widget=forms.PasswordInput(
            attrs={'class': 'form-control form-control-lg',
                   'placeholder': 'Password Confirmation'}),
    )

    class Meta:
        model = get_user_model()
        fields = ('username', 'email',)

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Email'
            })
        }


class UserLoginForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(
        attrs={"class": "form-control form-control-lg",
               "placeholder": "Username"}))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={"class": "form-control form-control-lg",
                   "placeholder": "Password"}
        ),
    )


class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Email'
    }))


class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'New Password'
        }), label="New Password"
    )
    new_password2 = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Confirm New Password'
        }), label="Confirm New Password"
    )


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Old Password'
        }), label="New Password"
    )
    new_password1 = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'New Password'
        }), label="New Password"
    )
    new_password2 = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Confirm New Password'
        }), label="Confirm New Password"
    )


class DishSearchForm(forms.ModelForm):
    name = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Pizza",
            }
        ),
    )

    class Meta:
        model = Dish
        fields = ["name", ]


class OrderUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'name',
            'phone_number',
            'email',
            'address',
            'asked_date_delivery',
        ]
        labels = {
            'asked_date_delivery': 'Delivery time',
        }
        widgets = {
            'asked_date_delivery': forms.DateTimeInput(
                attrs={'type': 'datetime-local',
                       'id': 'id_asked_date_delivery'}),
            'email': forms.EmailInput(
                attrs={'placeholder': 'E-Mail (Optional)'}),
            "phone_number": forms.TextInput(
                attrs={'placeholder': 'e.g. +12125552368'}),
        }

    def __init__(self, *args, **kwargs):
        customer = kwargs.pop('customer')
        super().__init__(*args, **kwargs)
        self.kyiv_time = timezone.now() + timezone.timedelta(hours=3)

        if customer.is_authenticated:
            if customer.first_name and customer.last_name:
                self.fields['name'].initial = (
                    f"{customer.first_name} {customer.last_name}"
                )
            elif customer.first_name:
                self.fields["name"].initial = customer.first_name

            if customer.phone_number:
                self.fields['phone_number'].initial = customer.phone_number
            if customer.email:
                self.fields['email'].initial = customer.email
            if customer.address:
                self.fields['address'].initial = customer.address

        self.fields["asked_date_delivery"].initial = (
                self.kyiv_time + timezone.timedelta(minutes=33)
        )

    def clean_name(self):
        return customer_name_validator(self.cleaned_data.get("name"))

    def clean_phone_number(self):
        return customer_phone_number_validator(
            self.cleaned_data.get("phone_number")
        )

    def clean_address(self):
        return customer_address_validator(self.cleaned_data.get("address"))

    def clean_asked_date_delivery(self):
        asked_date_delivery = self.cleaned_data.get("asked_date_delivery")
        if not asked_date_delivery:
            raise forms.ValidationError("Delivery time is required")

        if asked_date_delivery < self.kyiv_time + timezone.timedelta(
                minutes=30
        ):
            raise forms.ValidationError(
                "Time should beat least 30 minutes from now"
            )

        return asked_date_delivery
