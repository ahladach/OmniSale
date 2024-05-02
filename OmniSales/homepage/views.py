from django.shortcuts import render, redirect
from django.db.models import Sum, F
from django.utils import timezone
from transactions.models import SaleItem, SaleBill
from inventory.models import Stock
from datetime import datetime, timedelta, time
from django.http import JsonResponse
from django.views.generic import TemplateView, View
import csv
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth import login
from .forms import UpdatePasswordForm

def update_password(request):
    if request.method == 'POST':
        form = UpdatePasswordForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Your password has been updated successfully.')
            return redirect('login')
    else:
        form = UpdatePasswordForm()

    return render(request, 'update_password.html', {'form': form})

def home_view(request):
    # Get the current time
    current_time = datetime.now().time()

    # Determine the greeting based on the time of day
    if current_time < time(12, 0):
        greeting = "Good morning"
    elif current_time < time(18, 0):
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    print("Greeting:", greeting)

    # Get the current week's start and end dates
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # Generate a list of dates for the current week
    dates = [start_of_week + timedelta(days=x) for x in range(7)]

    # Fetch sales data for the current week
    sales_data = SaleItem.objects.filter(
        billno__time__date__range=[start_of_week, end_of_week]
    ).values('billno__time__date').annotate(total_sales=Sum('totalprice')).order_by('billno__time__date')

    # Create a dictionary to store sales data for each date
    sales_dict = {data['billno__time__date']: float(data['total_sales']) for data in sales_data}

    # Prepare data and labels for the line graph
    sales_labels = [date.strftime('%Y-%m-%d') for date in dates]
    sales_values = [sales_dict.get(date, 0) for date in dates]
    sales_max = max(sales_values) if sales_values else 0

    print("Sales labels:", sales_labels)
    print("Sales values:", sales_values)

    # Get products that are running out of stock
    low_stock_products = Stock.objects.filter(quantity__lt=F('threshold'), is_deleted=False)

    today = datetime.now().date()
    selected_date = request.GET.get('date', datetime.now().date())

    products_sold = SaleItem.objects.filter(
        billno__time__date=selected_date
    ).values('product__product').annotate(
        total_quantity=Sum('quantity'),
        total_price=Sum('totalprice')
    ).order_by('-total_quantity')

    # Fetch top 3 sales products of the day
    top_products = SaleItem.objects.filter(
        billno__time__date=today
    ).values('product__product').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:3]

    context = {
        'greeting': greeting,
        'sales_data': sales_values,
        'sales_labels': sales_labels,
        'sales_max': sales_max,
        'low_stock_products': low_stock_products,
        'top_products': top_products,
        'selected_date': selected_date,
        'products_sold': products_sold,
    }
    return render(request, 'home.html', context)

def get_sales_data(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Convert start_date and end_date to datetime objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    # Generate a list of dates for the selected date range
    dates = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

    sales_data = SaleItem.objects.filter(
        billno__time__date__range=[start_date, end_date]
    ).values('billno__time__date').annotate(total_sales=Sum('totalprice')).order_by('billno__time__date')

    # Create a dictionary to store sales data for each date
    sales_dict = {data['billno__time__date']: float(data['total_sales']) for data in sales_data}

    # Prepare data and labels for the line graph
    sales_labels = [date.strftime('%Y-%m-%d') for date in dates]
    sales_values = [sales_dict.get(date, 0) for date in dates]

    print("Sales labels (get_sales_data):", sales_labels)
    print("Sales values (get_sales_data):", sales_values)

    data = {
        'sales_labels': sales_labels,
        'sales_values': sales_values,
    }
    return JsonResponse(data)

@require_POST
def generate_sales_report(request):
    selected_date = request.POST.get('selected_date')
    # Get all available sale dates
    sale_dates = SaleItem.objects.values_list('billno__time__date', flat=True).distinct()

    # Create a response object with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'

    # Create a CSV writer
    writer = csv.writer(response)

    # Write the header row
    writer.writerow(['Date', 'Product', 'Quantity Sold'])

    # Iterate over each sale date and generate report data
    for sale_date in sale_dates:
        products_sold = SaleItem.objects.filter(
            billno__time__date=sale_date
        ).values('product__product').annotate(total_quantity=Sum('quantity'))

        # Write the data rows for each product sold on the current date
        for product in products_sold:
            writer.writerow([sale_date, product['product__product'], product['total_quantity']])

    return response

class AboutView(TemplateView):
    template_name = "about.html"