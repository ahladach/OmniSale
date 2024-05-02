from django import forms
from .models import Stock

class StockForm(forms.ModelForm):
    code = forms.CharField(max_length=5, required=False, widget=forms.TextInput(attrs={'readonly': True}))

    class Meta:
        model = Stock
        fields = ['category', 'brand', 'product', 'code', 'units', 'quantity', 'threshold']
        widgets = {
            'threshold': forms.NumberInput(attrs={'required': False}),
        }