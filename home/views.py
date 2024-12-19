from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.db.models import Sum
from django.utils import timezone
from django.db.models.functions import TruncDay, TruncMonth
import traceback
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView
from .models import *
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetConfirmView, PasswordResetView
from admin_datta.forms import RegistrationForm, LoginForm, UserPasswordChangeForm, UserPasswordResetForm, UserSetPasswordForm
import json
from django.shortcuts import get_object_or_404



def home(request):
    return render(request, 'pages/home.html')

@login_required(login_url='/accounts/login/')
def submit_sales(request):
    if request.method == 'POST':
        try:
            # Get totals
            total_fedha = request.POST.get('totalFedha')
            total_fedha_words = request.POST.get('totalFedhaWords')
            counted_money = request.POST.get('countedMoney')
            difference = request.POST.get('difference')

            # Get product data
            for key in request.POST.keys():
                if key.startswith('products['):
                    product_data = json.loads(request.POST.get(key))
                    product = Product.objects.get(id=product_data['productId'])
                    
                    # Create Sales record with user and shop
                    Sales.objects.create(
                        product=product,  # Pass the Product instance instead of ID
                        remainingJana=product_data['previousBalance'],
                        received=product_data['received'],
                        given=product_data['sold'],
                        total=product_data['total'],
                        sold=product_data['soldAmount'],
                        remaining=product_data['remainingBalance'],
                        spoiled=product_data['damaged'],
                        amount=product_data['cashAmount'],
                        counted_amount=counted_money,
                        difference=difference,
                        user=request.user,
                        shop=request.user.userprofile.shop
                    )

            return JsonResponse({'status': 'success', 'message': 'Data submitted successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required(login_url='/accounts/login/')
@csrf_exempt
def expense_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            expenses = data.get('expenses', [])
            jumla_ya_matumizi = data.get('jumlaYaMatumizi', 0)

            for expense in expenses:
                purpose = expense.get('purpose')
                amount = expense.get('value', 0)

                Expenses.objects.create(
                    purpose=purpose,
                    cost=amount,
                    user_regst=request.user.username,
                    shop=request.user.userprofile.shop
                )

            return JsonResponse({'status': 'success', 'message': 'Expenses recorded successfully.'})
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Method not allowed.'}, status=405)

@login_required(login_url='/accounts/login/')
def index(request):
    # Get today's date
    today = timezone.now().date()
    
    # Calculate daily sales
    daily_sales = Sales.objects.filter(
        created_at__date=today
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate monthly sales
    first_day_of_month = today.replace(day=1)
    monthly_sales = Sales.objects.filter(
        created_at__date__gte=first_day_of_month,
        created_at__date__lte=today
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate yearly sales
    first_day_of_year = today.replace(month=1, day=1)
    yearly_sales = Sales.objects.filter(
        created_at__date__gte=first_day_of_year,
        created_at__date__lte=today
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'segment': 'dashboard',
        'daily_sales': daily_sales,
        'monthly_sales': monthly_sales,
        'yearly_sales': yearly_sales,
    }
    return render(request, "pages/index.html", context)

@login_required(login_url='/accounts/login/')
def sales(request):
    products = Product.objects.all()
    expense_purpose = ExpensePurpose.objects.all()
    expense_purpose = Sales.objects.all()
    
    # Get suppliers from the supplier group associated with the user's shop
    suppliers = []
    try:
        supplier_group = Group.objects.get(name='Supplier')
        suppliers = User.objects.filter(
            groups=supplier_group,
            userprofile__shop=request.user.userprofile.shop
        )
    except Group.DoesNotExist:
        # Create the Supplier group if it doesn't exist
        supplier_group = Group.objects.create(name='Supplier')
    
    context = {
        'segment': 'Sales',
        'products': products,
        'expense_purpose': expense_purpose,
        'suppliers': suppliers
    }
    return render(request, "pages/sales.html", context)

@login_required
def supplier(request):
  context = {
    'segment': 'supplier'
  }
  return render(request, "pages/supplier.html", context)

@login_required(login_url='/accounts/login/')
def table(request):
  context = {
    'segment': 'table'
  }
  return render(request, "pages/dynamic-tables.html", context)

@login_required(login_url='/accounts/login/')
def store(request):
    if request.method == 'POST':
        try:
            received_liters = request.POST.get('received_liters')
            given_liters = request.POST.get('given_liters')
            from_shop_id = request.POST.get('from_shop')
            to_shop_id = request.POST.get('to_shop')

            print(f"Received POST data: received_liters={received_liters}, given_liters={given_liters}, from_shop={from_shop_id}, to_shop={to_shop_id}")

            # Handle received liters
            if received_liters and from_shop_id and received_liters.strip():
                try:
                    received_liters = float(received_liters)
                    from_shop = Shop.objects.get(id=from_shop_id)
                    
                    print(f"Processing received liters: {received_liters} from shop {from_shop.name}")
                    
                    record = StoreTransfer.get_or_create_daily_record(
                        user=request.user,
                        from_shop=from_shop
                    )
                    
                    record.received_liters += received_liters
                    record.save()
                    print(f"Updated received record: {record}")
                except ValueError as e:
                    print(f"Error processing received liters: {e}")
                    return JsonResponse({'status': 'error', 'message': 'Invalid received liters value'})

            # Handle given liters
            if given_liters and to_shop_id and given_liters.strip():
                try:
                    given_liters = float(given_liters)
                    to_shop = Shop.objects.get(id=to_shop_id)
                    
                    print(f"Processing given liters: {given_liters} to shop {to_shop.name}")
                    
                    record = StoreTransfer.get_or_create_daily_record(
                        user=request.user,
                        to_shop=to_shop
                    )
                    
                    record.given_liters += given_liters
                    record.save()
                    print(f"Updated given record: {record}")
                except ValueError as e:
                    print(f"Error processing given liters: {e}")
                    return JsonResponse({'status': 'error', 'message': 'Invalid given liters value'})

            return redirect('store')
        except Exception as e:
            print(f"Error in store view: {str(e)}")
            print(traceback.format_exc())
            # toast.error(str(e))
            return HttpResponse({'status': 'error', 'message': str(e)})

    # Get filter parameters
    shop_id = request.GET.get('shop')
    user_id = request.GET.get('user')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    # Start with all transfers
    transfers = StoreTransfer.objects.all().order_by('-date_created')

    # Apply filters
    if shop_id:
        transfers = transfers.filter(models.Q(from_shop_id=shop_id) | models.Q(to_shop_id=shop_id))
    if user_id:
        transfers = transfers.filter(user_id=user_id)
    if date_from:
        transfers = transfers.filter(date_created__gte=date_from)
    if date_to:
        transfers = transfers.filter(date_created__lte=date_to)

    # Calculate totals
    total_received = transfers.aggregate(Sum('received_liters'))['received_liters__sum'] or 0
    total_given = transfers.aggregate(Sum('given_liters'))['given_liters__sum'] or 0

    # Get all shops and users for filters
    shops = Shop.objects.all()
    users = User.objects.filter(storetransfer__isnull=False).distinct()
    
    context = {
        'segment': 'store',
        'shops': shops,
        'transfers': transfers,
        'users': users,
        'total_received': total_received,
        'total_given': total_given,
        'selected_shop': shop_id,
        'selected_user': user_id,
        'selected_date_from': date_from,
        'selected_date_to': date_to,
    }
    return render(request, "pages/store.html", context)

@login_required(login_url='/accounts/login/')
def analytics(request):
    # Get filter parameters
    shop_id = request.GET.get('shop')
    user_id = request.GET.get('user')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    # Start with all sales
    sales = Sales.objects.all()

    # Apply filters
    if shop_id:
        sales = sales.filter(shop_id=shop_id)
    if user_id:
        sales = sales.filter(user_id=user_id)
    if date_from:
        sales = sales.filter(created_at__gte=date_from)
    if date_to:
        sales = sales.filter(created_at__lte=date_to)

    # Calculate summary statistics
    total_sales = sales.aggregate(Sum('amount'))['amount__sum'] or 0
    total_received = sales.aggregate(Sum('received'))['received__sum'] or 0
    total_spoiled = sales.aggregate(Sum('spoiled'))['spoiled__sum'] or 0
    total_difference = sales.aggregate(Sum('difference'))['difference__sum'] or 0
    
    # Get expenses for the same period
    expenses = Expenses.objects.all()
    if shop_id:
        expenses = expenses.filter(shop_id=shop_id)
    if date_from:
        expenses = expenses.filter(date_created__gte=date_from)
    if date_to:
        expenses = expenses.filter(date_created__lte=date_to)
    
    total_expenses = expenses.aggregate(Sum('cost'))['cost__sum'] or 0

    # Get all shops and non-supplier users for the filter dropdowns
    shops = Shop.objects.all()
    supplier_group = Group.objects.get(name='Supplier')
    users = User.objects.exclude(groups=supplier_group).filter(sales__isnull=False).distinct()

    context = {
        'segment': 'analytics',
        'sales': sales,
        'total_sales': total_sales,
        'total_expenses': total_expenses,
        'total_received': total_received,
        'total_spoiled': total_spoiled,
        'total_difference': total_difference,
        'shops': shops,
        'users': users,
    }
    
    return render(request, 'pages/analytics.html', context)

# Authentication
class UserLoginView(LoginView):
  template_name = 'accounts/login.html'
  form_class = LoginForm

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Get the selected shop and create UserProfile
            shop = form.cleaned_data.get('shop')
            group = form.cleaned_data.get('group')
            
            # Create UserProfile
            UserProfile.objects.create(user=user, shop=shop)
            
            # Add user to the selected group
            user.groups.add(group)
            
            print('Account created successfully!')
            return redirect('/accounts/login/')
        else:
            print("Register failed!")
    else:
        form = RegistrationForm()

    context = { 'form': form }
    return render(request, 'accounts/register.html', context)

def logout_view(request):
  logout(request)
  return redirect('/accounts/login/')

class UserPasswordResetView(PasswordResetView):
  template_name = 'accounts/password_reset.html'
  form_class = UserPasswordResetForm

class UserPasswordResetConfirmView(PasswordResetConfirmView):
  template_name = 'accounts/password_reset_confirm.html'
  form_class = UserSetPasswordForm

class UserPasswordChangeView(PasswordChangeView):
  template_name = 'accounts/password_change.html'
  form_class = UserPasswordChangeForm

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            shop_id = request.POST.get('shop')
            shop = Shop.objects.get(id=shop_id)
            UserProfile.objects.create(user=user, shop=shop)
            return redirect('login')
    else:
        form = RegistrationForm()
    
    shops = Shop.objects.all()
    return render(request, 'accounts/register.html', {'form': form, 'shops': shops})

@login_required
def shop_report(request, shop_id):
    shop = Shop.objects.get(id=shop_id)
    sales = Sales.objects.filter(shop=shop)
    # Add your report logic here
    return render(request, 'reports/shop_report.html', {'sales': sales, 'shop': shop})

@login_required
def user_report(request, user_id):
    user_sales = Sales.objects.filter(user_id=user_id)
    # Add your report logic here
    return render(request, 'reports/user_report.html', {'sales': user_sales})

@login_required(login_url='/accounts/login/')
def submit_supplier_data(request):
    if request.method == 'POST':
        try:
            supplier_id = request.POST.get('supplier_id')
            liter = float(request.POST.get('liter'))
            
            supplier = get_object_or_404(User, id=supplier_id)
            
            # Create supplier data record
            SupplierData.objects.create(
                name=supplier.username,
                liter=liter,
                staff=request.user
            )
            
            # Get the first product (assuming it's the main product for suppliers)
            product = Product.objects.first()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Supplier data submitted successfully!',
                'product_id': product.id,
                'liter': liter
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)

@login_required(login_url='/accounts/login/')
def supplier_view(request):
    # Get user's group
    is_admin = request.user.groups.filter(name='Admin').exists()
    
    # Base queryset
    queryset = SupplierData.objects.all()
    
    # Filter by user if not admin
    if not is_admin:
        queryset = queryset.filter(staff=request.user)
    
    # Get date filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    period = request.GET.get('period', 'month')
    
    today = timezone.now()
    
    # Apply date filters if provided
    if start_date:
        start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d')
        start_date = timezone.make_aware(start_date)
        queryset = queryset.filter(receivedtime__gte=start_date)
    else:
        if period == 'week':
            start_date = today - timezone.timedelta(days=7)
        elif period == 'year':
            start_date = today - timezone.timedelta(days=365)
        else:  # month
            start_date = today - timezone.timedelta(days=30)
        queryset = queryset.filter(receivedtime__gte=start_date)
    
    if end_date:
        end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d')
        end_date = timezone.make_aware(end_date)
        end_date = end_date + timezone.timedelta(days=1)  # Include the end date
        queryset = queryset.filter(receivedtime__lt=end_date)
    else:
        end_date = today
    
    # Set current period text
    if start_date and end_date:
        current_period = f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"
    elif period == 'week':
        current_period = 'This Week'
    elif period == 'year':
        current_period = 'This Year'
    else:
        current_period = 'This Month'
    
    # Calculate statistics
    period_data = queryset
    total_liters = period_data.aggregate(total=models.Sum('liter'))['total'] or 0
    
    # Calculate growth (comparing with previous period)
    time_diff = end_date - start_date
    previous_start = start_date - time_diff
    previous_data = SupplierData.objects.filter(
        receivedtime__gte=previous_start,
        receivedtime__lt=start_date
    )
    if not is_admin:
        previous_data = previous_data.filter(staff=request.user)
    
    previous_liters = previous_data.aggregate(total=models.Sum('liter'))['total'] or 0
    liter_growth = ((total_liters - previous_liters) / previous_liters * 100) if previous_liters else 0
    
    # Calculate revenue (assuming a fixed price per liter)
    price_per_liter = 1000  # Set your price here
    total_revenue = total_liters * price_per_liter
    previous_revenue = previous_liters * price_per_liter
    revenue_growth = ((total_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue else 0
    
    # Get supply trend data
    from django.db.models.functions import TruncDay, TruncMonth
    
    if (end_date - start_date).days <= 31:
        trend_data = queryset.annotate(
            date=TruncDay('receivedtime')
        ).values('date').annotate(
            total=models.Sum('liter')
        ).order_by('date')
        trend_labels = [d['date'].strftime('%d %b') for d in trend_data]
    else:
        trend_data = queryset.annotate(
            date=TruncMonth('receivedtime')
        ).values('date').annotate(
            total=models.Sum('liter')
        ).order_by('date')
        trend_labels = [d['date'].strftime('%b %Y') for d in trend_data]
    
    trend_values = [float(d['total']) for d in trend_data]
    
    # Get top suppliers data
    top_suppliers = queryset.values('name').annotate(
        total=models.Sum('liter')
    ).order_by('-total')[:5]
    
    top_suppliers_labels = [s['name'] for s in top_suppliers]
    top_suppliers_data = [float(s['total']) for s in top_suppliers]
    
    # Get months for filter
    months = [
        (1, 'January'), (2, 'February'), (3, 'March'),
        (4, 'April'), (5, 'May'), (6, 'June'),
        (7, 'July'), (8, 'August'), (9, 'September'),
        (10, 'October'), (11, 'November'), (12, 'December')
    ]
    
    # Add revenue to queryset
    supplier_data = period_data.order_by('-receivedtime')
    for record in supplier_data:
        record.revenue = record.liter * price_per_liter
    
    context = {
        'total_liters': total_liters,
        'liter_growth': round(liter_growth, 1),
        'total_revenue': total_revenue,
        'revenue_growth': round(revenue_growth, 1),
        'total_suppliers': period_data.values('name').distinct().count(),
        'current_period': current_period,
        'supply_trend_data': trend_values,
        'supply_trend_labels': trend_labels,
        'top_suppliers_data': top_suppliers_data,
        'top_suppliers_labels': top_suppliers_labels,
        'months': months,
        'supplier_data': supplier_data,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'pages/supplier.html', context)