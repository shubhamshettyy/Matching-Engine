from django.shortcuts import render

# Create your views here.


def order(request):
    # context = {
    #     'posts': Post.objects.all()
    # }
    return render(request, 'stocks/order.html')
