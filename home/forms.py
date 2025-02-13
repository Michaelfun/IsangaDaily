from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, UsernameField, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext_lazy as _
from .models import Shop, Product, ExpensePurpose, ShopProductPrice, UserProfile, Expenses


class RegistrationForm(UserCreationForm):
  password1 = forms.CharField(
      label=_("Password"),
      widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
  )
  password2 = forms.CharField(
      label=_("Confirm Password"),
      widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
  )

  shop = forms.ModelChoiceField(
      queryset=Shop.objects.all(),
      widget=forms.Select(attrs={
          'class': 'form-control',
          'placeholder': 'Select Shop'
      })
  )

  group = forms.ModelChoiceField(
      queryset=Group.objects.all(),
      widget=forms.Select(attrs={
          'class': 'form-control',
          'placeholder': 'Select Role'
      })
  )

  class Meta:
    model = User
    fields = ('username', 'email', 'password1', 'password2', 'shop', 'group')

    widgets = {
      'username': forms.TextInput(attrs={
          'class': 'form-control',
          'placeholder': 'Username'
      }),
      'email': forms.EmailInput(attrs={
          'class': 'form-control',
          'placeholder': 'Email'
      })
    }


class LoginForm(AuthenticationForm):
    username = UsernameField(
        label=_("Your Username"), 
        widget=forms.TextInput(attrs={
            "class": "form-control", 
            "placeholder": "Username"
        })
    )
    password = forms.CharField(
        label=_("Your Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control", 
            "placeholder": "Password"
        }),
    )
    selected_shop = forms.ModelChoiceField(
        queryset=Shop.objects.all(),
        required=False,
        empty_label="Select Shop",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Select Shop'
        })
    )

    remember = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['selected_shop'].widget.attrs['style'] = 'display: none;'


class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email'
    }))

class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'New Password'
    }), label="New Password")
    new_password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Confirm New Password'
    }), label="Confirm New Password")
    

class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Old Password'
    }), label='Old Password')
    new_password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'New Password'
    }), label="New Password")
    new_password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Confirm New Password'
    }), label="Confirm New Password")

class CustomUserCreationForm(UserCreationForm):
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'default_price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'default_price': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ExpensePurposeForm(forms.ModelForm):
    class Meta:
        model = ExpensePurpose
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['name', 'location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ShopProductPriceForm(forms.ModelForm):
    class Meta:
        model = ShopProductPrice
        fields = ['product', 'shop', 'price']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'shop': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expenses
        fields = ['purpose', 'cost', 'shop']
        widgets = {
            'purpose': forms.TextInput(attrs={'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'shop': forms.Select(attrs={'class': 'form-control'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['shop']
        widgets = {
            'shop': forms.Select(attrs={'class': 'form-control'}),
        }