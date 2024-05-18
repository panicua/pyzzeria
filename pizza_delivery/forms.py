from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, \
    PasswordResetForm, SetPasswordForm, PasswordChangeForm, UsernameField
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from pizza_delivery.models import Dish, Order
from django.utils import timezone


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
                   "placeholder": "Password"}),
    )


class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Email'
    }))


class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(max_length=50,
                                    widget=forms.PasswordInput(attrs={
                                        'class': 'form-control form-control-lg',
                                        'placeholder': 'New Password'
                                    }), label="New Password")
    new_password2 = forms.CharField(max_length=50,
                                    widget=forms.PasswordInput(attrs={
                                        'class': 'form-control form-control-lg',
                                        'placeholder': 'Confirm New Password'
                                    }), label="Confirm New Password")


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(max_length=50,
                                   widget=forms.PasswordInput(attrs={
                                       'class': 'form-control form-control-lg',
                                       'placeholder': 'Old Password'
                                   }), label="New Password")
    new_password1 = forms.CharField(max_length=50,
                                    widget=forms.PasswordInput(attrs={
                                        'class': 'form-control form-control-lg',
                                        'placeholder': 'New Password'
                                    }), label="New Password")
    new_password2 = forms.CharField(max_length=50,
                                    widget=forms.PasswordInput(attrs={
                                        'class': 'form-control form-control-lg',
                                        'placeholder': 'Confirm New Password'
                                    }), label="Confirm New Password")


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

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if not name:
            raise forms.ValidationError("Name is required")
        if len(name) < 2:
            raise forms.ValidationError(
                "Name must be at least 2 characters long"
            )
        if not name.isalpha():
            raise forms.ValidationError("Name must contain only letters")
        return name

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if not phone_number:
            raise forms.ValidationError("Phone number is required")
        return phone_number

    def clean_address(self):
        address = self.cleaned_data.get("address")
        if not address:
            raise forms.ValidationError("Address is required")

        if len(address) < 10:
            raise forms.ValidationError(
                "Address must be at least 10 characters long"
            )

        if len(address) > 255:
            raise forms.ValidationError(
                "Address must be at most 255 characters long"
            )

        letters = [letter for letter in address if letter.isalpha()]
        if len(letters) < 8:
            raise forms.ValidationError(
                "Address must contain at least 8 letters"
            )

        digits = [digit for digit in address if digit.isdigit()]
        if len(digits) < 1:
            raise forms.ValidationError(
                "Address must contain at least 1 digit"
            )
        return address

    def clean_asked_date_delivery(self):
        asked_date_delivery = self.cleaned_data.get("asked_date_delivery")
        kyiv_time = timezone.now() + timezone.timedelta(hours=3)
        if not asked_date_delivery:
            raise forms.ValidationError("Delivery time is required")

        if asked_date_delivery < kyiv_time + timezone.timedelta(minutes=30):
            raise forms.ValidationError("Time should beat least 30 minutes from now")

        return asked_date_delivery

    # 'asked_date_delivery' validated on frontend with JS
