from django.db import models
from inventory.models import Stock
from django.db.models import Q
from decimal import Decimal
import json

class Supplier(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=10, unique=True)
    address = models.CharField(max_length=200)
    email = models.EmailField(max_length=254, unique=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name
class PurchaseBill(models.Model):
    billno = models.AutoField(primary_key=True)
    time = models.DateTimeField(auto_now=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchasesupplier')

    def __str__(self):
        return f"Bill no: {self.billno}"

    def get_total_price(self):
        total = 0
        for item in self.purchaseitems.all():
            print(f"PurchaseItem: {item}")
            total += item.totalprice
        return total
        
    def get_total_quantity(self):
        return sum(item.quantity for item in self.purchaseitems.all())

class PurchaseItem(models.Model):
    billno = models.ForeignKey(PurchaseBill, on_delete=models.CASCADE, related_name='purchaseitems')
    product = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='purchaseitems')
    quantity = models.PositiveIntegerField(default=1)
    perprice = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    totalprice = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Bill no: {self.billno.billno}, Item = {self.product.product}"

class PurchaseBillDetails(models.Model):
    billno = models.ForeignKey(PurchaseBill, on_delete=models.CASCADE, related_name='purchasedetailsbillno')
    eway = models.CharField(max_length=50, blank=True, null=True)
    veh = models.CharField(max_length=50, blank=True, null=True)
    destination = models.CharField(max_length=50, blank=True, null=True)
    po = models.CharField(max_length=50, blank=True, null=True)
    cgst = models.CharField(max_length=50, blank=True, null=True)
    sgst = models.CharField(max_length=50, blank=True, null=True)
    igst = models.CharField(max_length=50, blank=True, null=True)
    cess = models.CharField(max_length=50, blank=True, null=True)
    tcs = models.CharField(max_length=50, blank=True, null=True)
    total = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Bill no: {self.billno.billno}"

class SaleBill(models.Model):
    billno = models.AutoField(primary_key=True)
    time = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=12)
    email = models.EmailField(max_length=254)
    address = models.CharField(max_length=200)

    def __str__(self):
        return f"Bill no: {self.billno}"

    def get_items_list(self):
        return SaleItem.objects.filter(billno=self)

    def get_total_price(self):
        total = 0
        for item in self.salebillno.all():
            total += item.totalprice
        return total
    
    def get_total_payable(self):
        total_price = self.get_total_price()
        gst_rate = Decimal('0.01225')  # 1.225% GST
        gst_amount = total_price * gst_rate
        discount_percentage = self.saledetailsbillno.discount_percentage / 100
        discount_amount = total_price * discount_percentage
        total_payable = total_price + gst_amount - discount_amount
        return total_payable

class SaleItem(models.Model):
    billno = models.ForeignKey(SaleBill, on_delete=models.CASCADE, related_name='salebillno')
    product = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='saleitem', default=1)
    quantity = models.PositiveIntegerField(default=1)
    perprice = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    totalprice = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Bill no: {self.billno.billno}, Item = {self.product.product}"

class CartItem(models.Model):
    product = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    totalprice = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.product.product} - {self.quantity}"

    def get_total_price(self):
        return self.price * self.quantity

class Stock(models.Model):
    product = models.CharField(max_length=100, unique=True)
    brand = models.CharField(max_length=100)
    units = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.product

    def search_products(self, query):
        queryset = self.objects.filter(is_deleted=False)
        if query:
            queryset = queryset.filter(
                Q(category__icontains=query) |
                Q(product__icontains=query) |
                Q(brand__icontains=query)
            )
        return queryset

class SaleBillDetails(models.Model):
    billno = models.OneToOneField(SaleBill, on_delete=models.CASCADE, related_name='saledetailsbillno')
    eway = models.CharField(max_length=50, blank=True, null=True)
    veh = models.CharField(max_length=50, blank=True, null=True)
    destination = models.CharField(max_length=50, blank=True, null=True)
    po = models.CharField(max_length=50, blank=True, null=True)
    cgst = models.CharField(max_length=50, blank=True, null=True)
    sgst = models.CharField(max_length=50, blank=True, null=True)
    igst = models.CharField(max_length=50, blank=True, null=True)
    cess = models.CharField(max_length=50, blank=True, null=True)
    tcs = models.CharField(max_length=50, blank=True, null=True)
    total = models.CharField(max_length=50, blank=True, null=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return f"Bill no: {self.billno.billno}"


class SalePayment(models.Model):
    billno = models.ForeignKey(SaleBill, on_delete=models.CASCADE, related_name='salepayments')
    payment_details = models.TextField(default='{}')

    def __str__(self):
        return f"Bill no: {self.billno.billno}"

    def set_payment_details(self, payment_details):
        self.payment_details = json.dumps(payment_details)

    def get_payment_details(self):
        return json.loads(self.payment_details)
