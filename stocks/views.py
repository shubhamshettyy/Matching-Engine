from django.shortcuts import render
from .forms import OrderForm
# Create your views here.


def order(request):
    # context = {
    #     'posts': Post.objects.all()
    # }
    form = OrderForm()
    if request.method == 'POST':
        print(request.POST)
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
    context = {'form':form}
    return render(request, 'stocks/order.html', context)
