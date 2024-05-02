from django import forms
from django.forms import formset_factory
from .models import (
    Supplier,
    PurchaseBill,
    PurchaseItem,
    PurchaseBillDetails,
    SaleBill,
    SaleItem,
    SaleBillDetails,
    SalePayment
)
from inventory.models import Stock
from .models import PurchaseItem, PurchaseBillDetails
import random

# Form used to select a supplier
class SelectSupplierForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier'].queryset = Supplier.objects.filter(is_deleted=False)
        self.fields['supplier'].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = PurchaseBill
        fields = ['supplier']

# Form used to render a single purchase item form
class PurchaseItemForm(forms.Form):
    product = forms.CharField(label='Product', max_length=100)
    category = forms.CharField(label='Category', max_length=100)
    brand = forms.CharField(label='Brand', max_length=100, required=False)
    units = forms.CharField(label='Units', max_length=100, required=False)
    quantity = forms.IntegerField(label='Quantity', min_value=1)
    perprice = forms.DecimalField(label='Price per Unit', min_value=0, decimal_places=2)

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        category = cleaned_data.get('category')
        brand = cleaned_data.get('brand')
        units = cleaned_data.get('units')
        quantity = cleaned_data.get('quantity')
        # Validate the units field
        if not units:
            raise forms.ValidationError("Units field is required.")

        # Check if the product, category, brand, and units match any existing stock item
        stock_item = Stock.objects.filter(
            product__iexact=product,
            category__iexact=category,
            brand__iexact=brand,
            units__iexact=units
        ).first()

        if stock_item:
            print(f"Existing stock item found: {stock_item}")
            # Update the existing stock item's quantity
            stock_item.quantity += quantity
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
            Stock.objects.create(
                product=product,
                category=category,
                brand=brand,
                units=units,
                quantity=quantity,
                code=product_code
            )
            print(f"New stock item created with product code: {product_code}")

        return cleaned_data

PurchaseItemFormset = forms.formset_factory(PurchaseItemForm, extra=1)

class PurchaseDetailsForm(forms.ModelForm):
    class Meta:
        model = PurchaseBillDetails
        fields = ['eway', 'veh', 'destination', 'po', 'cgst', 'sgst', 'igst', 'cess', 'tcs', 'total']


# Form used for supplier
class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'phone', 'address', 'email']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].widget.attrs['maxlength'] = 12

class SaleForm(forms.ModelForm):
    discount_percentage = forms.DecimalField(
        label='Discount Percentage',
        min_value=0,
        max_value=100,
        decimal_places=2,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'pattern': r'[a-zA-Z\s]{1,50}', 'title': 'Alphabets and Spaces only', 'required': 'true'})
        self.fields['phone'].widget.attrs.update({'class': 'form-control', 'maxlength': '10', 'pattern': r'[0-9]{10}', 'title': 'Numbers only', 'required': 'true'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['address'].widget.attrs.update({'class': 'form-control', 'rows': '4'})
        

    class Meta:
        model = SaleBill
        fields = ['name', 'phone', 'address', 'email', 'discount_percentage']


class SaleItemForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Stock.objects.filter(is_deleted=False)
        self.fields['product'].widget.attrs.update({'class': 'form-control setprice stock', 'required': 'true'})
        self.fields['quantity'].widget.attrs.update({'class': 'form-control setprice quantity', 'min': '1', 'required': 'true'})

    class Meta:
        model = SaleItem
        fields = ['product', 'quantity']


SaleItemFormset = forms.formset_factory(SaleItemForm, extra=1)


class AddToCartForm(forms.Form):
    product_id = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}))
    price = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quantity'].initial = 1
        self.fields['price'].initial = 0


class SaleDetailsForm(forms.ModelForm):
    class Meta:
        model = SaleBillDetails
        fields = ['eway', 'veh', 'destination', 'po', 'cgst', 'sgst', 'igst', 'cess', 'tcs', 'total', 'discount_percentage']
        widgets = {
            'eway': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter E-Way Bill Number'}),
            'veh': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Vehicle Number'}),
            'destination': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Destination'}),
            'po': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter PO'}),
            'cgst': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter CGST'}),
            'sgst': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter SGST'}),
            'igst': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter IGST'}),
            'cess': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter CESS'}),
            'tcs': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter TCS'}),
            'total': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Total'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Discount Percentage'}),
        }

class SalePaymentForm(forms.ModelForm):
    payment_type = forms.ChoiceField(choices=[('cash', 'Cash'), ('card', 'Card')], widget=forms.Select(attrs={'class': 'form-control'}))
    payment_amount = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Payment Amount'}))
    card_type = forms.ChoiceField(choices=[('visa', 'Visa'), ('mastercard', 'Mastercard'), ('amex', 'American Express')], widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    card_number = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Card Number'}), required=False)
    card_expiry = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Card Expiry (MM/YY)'}), required=False)

    class Meta:
        model = SalePayment
        fields = ['payment_details']

    def __init__(self, *args, **kwargs):
        super(SalePaymentForm, self).__init__(*args, **kwargs)
        self.fields['card_type'].required = False
        self.fields['card_number'].required = False
        self.fields['card_expiry'].required = False

    def clean(self):
        cleaned_data = super().clean()
        payment_type = cleaned_data.get('payment_type')
        payment_amount = cleaned_data.get('payment_amount')
        card_type = cleaned_data.get('card_type')
        card_number = cleaned_data.get('card_number')
        card_expiry = cleaned_data.get('card_expiry')

        payment_details = {
            'payment_type': payment_type,
            'payment_amount': str(payment_amount),
            'card_type': card_type,
            'card_number': card_number,
            'card_expiry': card_expiry
        }

        cleaned_data['payment_details'] = payment_details

        return cleaned_data