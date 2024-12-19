from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views


urlpatterns = [
  path('', index, name='index'),
  path('sales/', sales, name='sales'),
  path('table/', table, name='table'),
  path('supplier/', supplier_view, name='supplier'),
  path('store/', store, name='store'),
  path('analytics/', analytics, name='analytics'),
  path('submit-sales/', submit_sales, name='submit_sales'),
  path('expense_view/', expense_view, name='expense_view'),

  # Authentication
  path('accounts/login/', UserLoginView.as_view(), name='login'),
  path('accounts/logout/', logout_view, name='logout'),
  path('accounts/register/', register, name='register'),
  path('accounts/password-change/', UserPasswordChangeView.as_view(), name='password_change'),
  path('accounts/password-change-done/', auth_views.PasswordChangeDoneView.as_view(
      template_name='accounts/password_change_done.html'
  ), name="password_change_done"),
  path('accounts/password-reset/',UserPasswordResetView.as_view(), name='password_reset'),
  path('accounts/password-reset-confirm/<uidb64>/<token>/', 
      UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
  path('accounts/password-reset-done/', auth_views.PasswordResetDoneView.as_view(
      template_name='accounts/password_reset_done.html'
  ), name='password_reset_done'),
  path('accounts/password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
      template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),

  path('submit-supplier-data/',submit_supplier_data, name='submit_supplier_data'),

]
