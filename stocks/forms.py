from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['id', 'stock_type', 'quantity', 'order_type']
        # widgets = {'price': forms.HiddenInput()}
        exclude= ['price']
        
