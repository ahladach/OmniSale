from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, CreateView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from .models import Stock
from .forms import StockForm
from django_filters.views import FilterView
from .filters import StockFilter
import random
 
class StockListView(FilterView):
    filterset_class = StockFilter
    queryset = Stock.objects.filter(is_deleted=False)
    template_name = 'inventory.html'
    paginate_by = 10
 
class StockCreateView(SuccessMessageMixin, CreateView):
    model = Stock
    form_class = StockForm
    template_name = "new_stock.html"
    success_url = '/inventory'
    success_message = "Stock has been created successfully"

    def form_valid(self, form):
        # Generate a unique product code
        while True:
            code = str(random.randint(40000, 99999))
            if not Stock.objects.filter(code=code).exists():
                form.instance.code = code
                break
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'New Stock'
        context["savebtn"] = 'Add to Inventory'
        return context

class StockUpdateView(SuccessMessageMixin, UpdateView):
    model = Stock
    form_class = StockForm
    template_name = "edit_stock.html"
    success_url = '/inventory'
    success_message = "Stock has been updated successfully"
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edit Stock'
        context["savebtn"] = 'Update Stock'
        context["delbtn"] = 'Delete Stock'
        return context
 
class StockDeleteView(View):
    template_name = "delete_stock.html"
    success_message = "Stock has been deleted successfully"
 
    def get(self, request, pk):
        stock = get_object_or_404(Stock, pk=pk)
        return render(request, self.template_name, {'object': stock})
 
    def post(self, request, pk):
        stock = get_object_or_404(Stock, pk=pk)
        stock.is_deleted = True
        stock.save()
        messages.success(request, self.success_message)
        return redirect('inventory')