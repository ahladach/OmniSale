import random
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal
from django.views.generic import (
    View,
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST
from .models import (
    PurchaseBill,
    Supplier,
    PurchaseItem,
    PurchaseBillDetails,
    SaleBill,
    SaleItem,
    SaleBillDetails,
    SalePayment
)
from .forms import (
    SelectSupplierForm,
    PurchaseItemFormset,
    PurchaseDetailsForm,
    SupplierForm,
    SaleForm,
    SaleItemFormset,
    SaleDetailsForm,
    SaleItemForm,
    SalePaymentForm
)
from inventory.models import Stock
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib import messages
from .models import PurchaseBill, PurchaseBillDetails, Stock
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from .forms import PurchaseItemFormset, PurchaseDetailsForm
from .models import PurchaseBill, PurchaseItem, Supplier, CartItem
from inventory.models import Stock
from django.forms.formsets import formset_factory
from django.template.loader import render_to_string
from django.http import JsonResponse
from decimal import Decimal, InvalidOperation

# shows a lists of all suppliers
class SupplierListView(ListView):
    model = Supplier
    template_name = "suppliers/suppliers_list.html"
    queryset = Supplier.objects.filter(is_deleted=False)
    paginate_by = 10

# used to add a new supplier
class SupplierCreateView(SuccessMessageMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    success_url = '/transactions/suppliers'
    success_message = "Supplier has been created successfully"
    template_name = "suppliers/edit_supplier.html"

    def form_valid(self, form):
        supplier = form.save(commit=False)
        supplier.save()
        messages.success(self.request, self.success_message)
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, "Failed to create a new supplier. Please check the form data.")
        return self.render_to_response(self.get_context_data(form=form))

# used to update a supplier's info
class SupplierUpdateView(SuccessMessageMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    success_url = '/transactions/suppliers'
    success_message = "Supplier details have been updated successfully"
    template_name = "suppliers/edit_supplier.html"

# used to delete a supplier
class SupplierDeleteView(View):
    template_name = "suppliers/delete_supplier.html"
    success_message = "Supplier has been deleted successfully"

    def get(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        return render(request, self.template_name, {'object': supplier})

    def post(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        supplier.is_deleted = True
        supplier.save()
        messages.success(request, self.success_message)
        return redirect('suppliers-list')

# used to view a supplier's profile
class SupplierView(View):
    def get(self, request, name):
        supplierobj = get_object_or_404(Supplier, name=name)
        bill_list = PurchaseBill.objects.filter(supplier=supplierobj)
        page = request.GET.get('page', 1)
        paginator = Paginator(bill_list, 10)
        try:
            bills = paginator.page(page)
        except PageNotAnInteger:
            bills = paginator.page(1)
        except EmptyPage:
            bills = paginator.page(paginator.num_pages)
        context = {
            'supplier': supplierobj,
            'bills': bills
        }
        return render(request, 'suppliers/supplier.html', context)

# used to select the supplier
class SelectSupplierView(View):
    form_class = SelectSupplierForm
    template_name = 'purchases/select_supplier.html'

    def get(self, request, *args, **kwargs):                                    # loads the form page
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):                                   # gets selected supplier and redirects to 'PurchaseCreateView' class
        form = self.form_class(request.POST)
        if form.is_valid():
            supplierid = request.POST.get("supplier")
            supplier = get_object_or_404(Supplier, id=supplierid)
            return redirect('new-purchase', supplier.pk)
        return render(request, self.template_name, {'form': form})


# shows the list of bills of all purchases
class PurchaseView(ListView):
    model = PurchaseBill
    template_name = "purchases/purchases_list.html"
    context_object_name = 'bills'
    ordering = ['-time']
    paginate_by = 10

class PurchaseCreateView(View):
    template_name = 'purchases/new_purchase.html'

    def get(self, request, pk):
        print("GET request received for PurchaseCreateView")
        formset = PurchaseItemFormset(request.GET or None)
        supplier = get_object_or_404(Supplier, pk=pk)
        print(f"Supplier: {supplier}")
        context = {
            'formset': formset,
            'supplier': supplier,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        print("POST request received for PurchaseCreateView")
        formset = PurchaseItemFormset(request.POST)
        supplier = get_object_or_404(Supplier, pk=pk)
        print(f"Supplier: {supplier}")

        if formset.is_valid():
            print("Formset is valid")
            # Create a new PurchaseBill object
            bill = PurchaseBill.objects.create(supplier=supplier)
            print(f"PurchaseBill created: {bill}")

            for form in formset:
                product = form.cleaned_data['product']
                category = form.cleaned_data['category']
                brand = form.cleaned_data['brand']
                units = form.cleaned_data['units']
                quantity = form.cleaned_data['quantity']
                perprice = form.cleaned_data['perprice']
                print(f"Form data: product={product}, category={category}, brand={brand}, units={units}, quantity={quantity}, perprice={perprice}")

                # Check if the product is present in the stock
                stock_item = Stock.objects.filter(
                    product__iexact=product,
                    category__iexact=category,
                    brand__iexact=brand,
                    units=units
                ).first()

                if stock_item:
                    print(f"Existing stock item found: {stock_item}")
                    # Update the existing stock item's quantity
                    #stock_item.quantity = stock_item.quantity+quantity
                    stock_item.save()
                    print(f"Stock item quantity updated: {stock_item.quantity}")
                else:
                    print("Creating a new stock item")
                    # Generate a unique product code
                    while True:
                        product_code = random.randint(45000, 70000)
                        if not Stock.objects.filter(code=product_code).exists():
                            break

                    # Create a new stock item
                    stock_item = Stock.objects.create(
                        product=product,
                        category=category,
                        brand=brand,
                        units=units,
                        quantity=quantity,
                        code=product_code
                    )
                    print(f"New stock item created: {stock_item}")

                # Create a new PurchaseItem and link it to the PurchaseBill
                purchase_item = PurchaseItem.objects.create(
                    billno=bill,
                    product=stock_item,
                    quantity=quantity,
                    perprice=perprice,
                    totalprice=quantity * perprice
                )
                print(f"PurchaseItem created: {purchase_item}")

            messages.success(request, "Purchased items have been registered successfully")
            return redirect('purchases-list')
        else:
            print(f"Formset is not valid: {formset.errors}")
            context = {
                'formset': formset,
                'supplier': supplier,
            }
            return render(request, self.template_name, context)
            
# used to delete a bill object
class PurchaseDeleteView(SuccessMessageMixin, DeleteView):
    model = PurchaseBill
    template_name = "purchases/delete_purchase.html"
    success_url = '/transactions/purchases'

    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        items = PurchaseItem.objects.filter(billno=self.object.billno)
        for item in items:
            stock = Stock.objects.filter(
                product=item.product.product,
                category=item.product.category
            ).first()
            if not stock.is_deleted:
                if stock.quantity >= item.quantity:
                    stock.quantity -= item.quantity
                    stock.save()
                else:
                    stock.quantity = 0
                    stock.is_deleted = True
                    stock.save()
        messages.success(self.request, "Purchase bill has been deleted successfully")
        return redirect(self.success_url)

class PurchaseUpdateView(UpdateView):
    model = PurchaseBill
    fields = ['supplier', 'date', 'items']
    template_name = 'transactions/purchase_update_form.html'
    success_url = reverse_lazy('transactions:purchases_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        return response

class SaleView(ListView):
    model = SaleBill
    template_name = "sales/sales_list.html"
    context_object_name = 'bills'
    ordering = ['-time']
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query) | queryset.filter(billno__icontains=search_query)
        return queryset

        return context

class SaleCreateView(View):
    template_name = 'sales/new_sale.html'
 
    def get(self, request):
        form = SaleForm()
        cart_items = CartItem.objects.all()
        total_price = sum(item.get_total_price() for item in cart_items)
        gst_rate = Decimal('0.01225')  # 1.225% GST
        gst_amount = total_price * gst_rate
        total_price_with_gst = total_price + gst_amount
 
        discount_percentage = Decimal('0')  # Default discount percentage
        discount_amount = Decimal('0')  # Default discount amount
        total_payable = total_price_with_gst
 
        if form.is_valid():
            discount_percentage = form.cleaned_data.get('discount_percentage', '0')
            discount_percentage = Decimal(discount_percentage)
            discount_amount = total_price * (discount_percentage / 100)
            total_payable = total_price_with_gst - discount_amount
 
        search_type = request.GET.get('search_type')
        search_item = request.GET.get('search_item')
        products = None
 
        if search_type == 'category' and search_item:
            products = Stock.objects.filter(is_deleted=False, category__icontains=search_item)
        elif search_type == 'product' and search_item:
            products = Stock.objects.filter(is_deleted=False, product__icontains=search_item)
 
        payment_methods = request.session.get('payment_methods', [{'payment_type': 'cash', 'payment_amount': 0}])
 
        context = {
            'form': form,
            'products': products,
            'cart_items': cart_items,
            'total_price': total_price,
            'gst_amount': gst_amount,
            'discount_amount': discount_amount,
            'total_payable': total_payable,
            'search_item': search_item,
            'payment_methods': payment_methods,
        }
        return render(request, self.template_name, context)
 
    def post(self, request):
        form = SaleForm(request.POST)
        cart_items = CartItem.objects.all()
        total_price = sum(item.get_total_price() for item in cart_items)
        gst_rate = Decimal('0.01225')  # 1.225% GST
        gst_amount = total_price * gst_rate
        discount_percentage = Decimal(request.POST.get('discount_percentage', 0)) / 100
        total_price_with_gst = total_price + gst_amount 
        discount_amount = total_price_with_gst * discount_percentage
        total_payable = total_price_with_gst - discount_amount
        final_total = total_payable

        payment_methods = []

        payment_count = int(request.POST.get('payment_count', 1))

        for i in range(1, payment_count + 1):
            payment_type = request.POST.get(f'payment_type_{i}')
            payment_amount = Decimal(request.POST.get(f'payment_amount_{i}', 0))
            card_type = request.POST.get(f'card_type_{i}') if payment_type == 'card' else None
            card_number = request.POST.get(f'card_number_{i}') if payment_type == 'card' else None
            card_expiry = request.POST.get(f'card_expiry_{i}') if payment_type == 'card' else None
                                                                                                                                                                                                    
            payment_methods.append({
                'payment_type': payment_type,
                'payment_amount': payment_amount,
                'card_type': card_type,
                'card_number': card_number,
                'card_expiry': card_expiry
            })

        request.session['payment_methods'] = payment_methods

        if form.is_valid():
            sale_bill = form.save(commit=False)
            sale_bill.save()

            # Create SaleBillDetails
            sale_bill_details = SaleBillDetails.objects.create(
                billno=sale_bill,
                eway=request.POST.get('eway', ''),
                veh=request.POST.get('veh', ''),
                destination=request.POST.get('destination', ''),
                po=request.POST.get('po', ''),
                cgst=request.POST.get('cgst', ''),
                sgst=request.POST.get('sgst', ''),
                igst=request.POST.get('igst', ''),
                cess=request.POST.get('cess', ''),
                tcs=request.POST.get('tcs', ''),
                total=str(total_payable),
                discount_percentage=discount_percentage * 100
            )

            # Create a single SalePayment object with payment details as JSON
            payment_details = []
            # Create SalePayment objects for each payment method
            for payment_method in payment_methods:
                payment_details = {
                    'payment_type': payment_method['payment_type'],
                    'payment_amount': str(payment_method['payment_amount']),
                    'card_type': payment_method['card_type'],
                    'card_number': payment_method['card_number'],
                    'card_expiry': payment_method['card_expiry']
                }

                sale_payment = SalePayment.objects.create(billno=sale_bill)
                sale_payment.set_payment_details(payment_details)
                sale_payment.save()

            for item in cart_items:
                sale_item = SaleItem.objects.create(
                    billno=sale_bill,
                    product=item.product,
                    quantity=item.quantity,
                    perprice=item.price,
                    totalprice=item.get_total_price()
                )
                sale_item.save()
 
                item.product.quantity -= item.quantity
                item.product.save()
 
            cart_items.delete()  # Clear the cart after completing the sale
 
            del request.session['payment_methods']  # Clear the payment methods from the session
 
            messages.success(request, "Sale completed successfully.")
            return redirect('sales-list')
        else:
            messages.error(request, "Failed to complete sale. Please check the form.")
 
        context = {
            'form': form,
            'products': None,
            'cart_items': cart_items,
            'total_price': total_price,
            'gst_amount': gst_amount,
            'discount_amount': discount_amount,
            'total_payable': final_total,
            'payment_methods': payment_methods,
        }
        return render(request, self.template_name, context)

def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity', '1')
        price = request.POST.get('price', '0')

        try:
            quantity = int(quantity)
        except ValueError:
            quantity = 1

        try:
            price = Decimal(price)
        except InvalidOperation:
            price = Decimal('0')

        product = get_object_or_404(Stock, id=product_id)
        cart_item, created = CartItem.objects.get_or_create(product=product)
        cart_item.quantity = quantity
        cart_item.price = price
        cart_item.totalprice = quantity * price
        cart_item.save()

        if not messages.get_messages(request):
            messages.success(request, "Product added to cart successfully.")
        return redirect('new-sale')

    return redirect('new-sale')

def remove_from_cart(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(CartItem, id=item_id)
        item.delete()

        if not messages.get_messages(request):
            messages.success(request, "Product removed from cart successfully.")
        return redirect('new-sale')

    return redirect('new-sale')

class SaleDeleteView(SuccessMessageMixin, DeleteView):
    model = SaleBill
    template_name = "sales/delete_sale.html"
    success_url = '/transactions/sales'

    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        items = SaleItem.objects.filter(billno=self.object.billno)
        for item in items:
            #stock = get_object_or_404(Stock, product=item.product)
            stock = Stock.objects.filter(
                product=item.product.product,
            ).first()
            if stock.is_deleted == False:
                stock.quantity += item.quantity
                stock.save()
        messages.success(self.request, "Sale bill has been deleted successfully")
        return super(SaleDeleteView, self).delete(*args, **kwargs) 
        
# used to display the purchase bill object
class PurchaseBillView(View):
    model = PurchaseBill
    template_name = "bill/purchase_bill.html"
    bill_base = "bill/bill_base.html"

    def get(self, request, billno):
        bill = PurchaseBill.objects.get(billno=billno)
        items = PurchaseItem.objects.filter(billno=billno)
        try:
            billdetails = PurchaseBillDetails.objects.get(billno=bill)
        except PurchaseBillDetails.DoesNotExist:
            billdetails = None
        context = {
            'bill': bill,
            'items': items,
            'billdetails': billdetails,
            'bill_base': self.bill_base,
        }
        return render(request, self.template_name, context)

    def post(self, request, billno):
        form = PurchaseDetailsForm(request.POST)
        bill = PurchaseBill.objects.get(billno=billno)
        if form.is_valid():
            billdetails, created = PurchaseBillDetails.objects.get_or_create(billno=bill)
            form = PurchaseDetailsForm(request.POST, instance=billdetails)
            form.save()
            messages.success(request, "Bill details have been modified successfully")
        else:
            messages.error(request, "Invalid form data")
        items = PurchaseItem.objects.filter(billno=billno)
        context = {
            'bill': bill,
            'items': items,
            'billdetails': billdetails,
            'bill_base': self.bill_base,
        }
        return render(request, self.template_name, context)

class SaleBillView(View):
    model = SaleBill
    template_name = "bill/sale_bill.html"
    bill_base = "bill/bill_base.html"

    def get(self, request, billno):
        bill = SaleBill.objects.get(billno=billno)
        items = SaleItem.objects.filter(billno=billno)
        billdetails = SaleBillDetails.objects.get(billno=billno)
        payments = SalePayment.objects.filter(billno=billno)
        payment_details = [payment.get_payment_details() for payment in payments]
        context = {
            'bill': bill,
            'items': items,
            'billdetails': billdetails,
            'payment_details': payment_details,
            'bill_base': self.bill_base,
        }
        return render(request, self.template_name, context)

    def post(self, request, billno):
        bill = SaleBill.objects.get(billno=billno)
        items = SaleItem.objects.filter(billno=billno)
        billdetails = SaleBillDetails.objects.get(billno=billno)
        form = SaleDetailsForm(request.POST, instance=billdetails)
        if form.is_valid():
            form.save()
            messages.success(request, "Bill details have been modified successfully")
        context = {
            'bill': bill,
            'items': items,
            'billdetails': billdetails,
            'bill_base': self.bill_base,
            'form': form,
        }
        return render(request, self.template_name, context)

def calculate_remaining_amount(request, total_payable):
    total_paid = Decimal(0)
    payment_methods = request.session.get('payment_methods', [])
    for payment_method in payment_methods:
        total_paid += Decimal(payment_method['payment_amount'])
    remaining_amount = total_payable - total_paid
    return remaining_amount
 
def add_payment(request):
    total_payable = Decimal(request.POST.get('total_payable', '0'))
    remaining_amount = calculate_remaining_amount(request, total_payable)
    return render(request, 'sales/add_payment.html', {'remaining_amount': remaining_amount})