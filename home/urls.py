from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views


urlpatterns = [
  path('', analytics, name='index'),
  path('sales/', sales, name='sales'),
  path('table/', table, name='table'),
  path('supplier/', supplier_view, name='supplier'),
  path('store/', store, name='store'),
  path('analytics/', analytics, name='analytics'),
  path('submit-sales/', submit_sales, name='submit_sales'),
  path('expense_view/', expense_view, name='expense_view'),

  # Authentication
  path('accounts/login/', login_view, name='login'),
  path('check-user-group/<str:username>/', check_user_group, name='check-user-group'),
  path('accounts/logout/', logout_view, name='logout'),
  path('accounts/register/', register, name='registration'),
  path('accounts/password-change/', UserPasswordChangeView.as_view(), name='password_change'),
  path('accounts/password-change-done/', auth_views.PasswordChangeDoneView.as_view(
      template_name='accounts/password_change_done.html'
  ), name="password_change_done"),
  path('accounts/password-reset/', UserPasswordResetView.as_view(), name='password_reset'),
  path('accounts/password-reset-confirm/<uidb64>/<token>/', 
      UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
  path('accounts/password-reset-done/', auth_views.PasswordResetDoneView.as_view(
      template_name='accounts/password_reset_done.html'
  ), name='password_reset_done'),
  path('accounts/password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
      template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
  path('accounts/check-user-group/<str:username>/', check_user_group, name='check-user-group'),

  path('submit-supplier-data/',submit_supplier_data, name='submit_supplier_data'),
  path('accounts/get-shops/', get_shops, name='get_shops'),

  path('export/sales/excel/', export_sales_excel, name='export_sales_excel'),
  path('export/sales/pdf/', export_sales_pdf, name='export_sales_pdf'),
  path('export/daily-analysis/excel/', export_daily_analysis_excel, name='export_daily_analysis_excel'),
  path('export/daily-analysis/pdf/', export_daily_analysis_pdf, name='export_daily_analysis_pdf'),

  path('products/', product_list, name='product_list'),
  path('products/create/', product_create, name='product_create'),
  path('products/<int:pk>/edit/', product_edit, name='product_edit'),
  path('products/<int:pk>/delete/', product_delete, name='product_delete'),
  
  # Loan endpoints
  path('api/loan/<int:loan_id>/', get_loan_data, name='get_loan_data'),
  path('loan/', loan_view, name='loan'),
  path('loan/<int:loan_id>/data/', get_loan_data, name='get_loan_data'),
  path('update-loan/', update_loan, name='update_loan'),

  path('expense-purposes/', expense_purpose_list, name='expense_purpose_list'),
  path('expense-purposes/create/', expense_purpose_create, name='expense_purpose_create'),
  path('expense-purposes/<int:pk>/edit/', expense_purpose_edit, name='expense_purpose_edit'),
  path('expense-purposes/<int:pk>/delete/', expense_purpose_delete, name='expense_purpose_delete'),

  path('shops/', shop_list, name='shop_list'),
  path('shops/create/', shop_create, name='shop_create'),
  path('shop-prices/', shop_price_list, name='shop_price_list'),
  path('shop-prices/create/', shop_price_create, name='shop_price_create'),
  path('shop-prices/<int:pk>/edit/', shop_price_edit, name='shop_price_edit'),
  path('shop-prices/<int:pk>/delete/', shop_price_delete, name='shop_price_delete'),

  path('loan/view/', loan_view, name='loan'), # Fix the incomplete URL pattern
]
