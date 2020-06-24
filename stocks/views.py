from django.shortcuts import render,redirect
from .forms import OrderForm
from .models import Order
import requests
from bs4 import BeautifulSoup
import requests_html
import lxml.html as lh
import re
from datetime import datetime
from datetime import timedelta
import time
import random
# Create your views here.



def stock_price(stock_name):
    url = 'https://in.finance.yahoo.com/quote/' + stock_name
    session = requests_html.HTMLSession()
    r = session.get(url)
    content = BeautifulSoup(r.content, 'lxml')
    try:
        price = str(content).split(
            'data-reactid="32"')[4].split('</span>')[0].replace('>', '')
    except IndexError as e:
        price = 0.00
    price = price or "0"
    try:
        price = float(price.replace(',', ''))
    except ValueError as e:
        price = 0.00
    time.sleep(1)
    return price


def order(request):
    # context = {
    #     'posts': Post.objects.all()
    # }
    prices = []
    stock_names = ["BHARTIARTL.NS", "ASHOKLEY.NS", "AUROPHARMA.NS", "RELIANCE.NS",
                   "TCS.NS", "BAJFINANCE.NS", "HINDUNILVR.NS", "IBN", "LT.BO", "ITC.BO"]
    # for stock in stock_names:
    #     prices.append(stock_price(stock))

    # print(prices)
    form = OrderForm()
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            stock_type = form.cleaned_data.get('stock_type')
            f=form.save(commit=False)
            f.price = stock_price(stock_type)
            # print(stock_type, f.price)
            f.save()
            return redirect('trades')

    context = {
        'form':form,
        'stock_names':stock_names,
        'prices':prices
    }
    return render(request, 'stocks/order.html', context)


randomIdStr = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'

def generate_id(length):
    rand_str = ''
    for i in range(length):
        rand_str = rand_str + \
            randomIdStr[random.randrange(0, len(randomIdStr))]

    return rand_str


def make_order(cust_id, trade_type, quantity, stock_code, stockprice):
    order = {"order_id": generate_id(7),
             "trade_type": trade_type,
             "quantity": quantity,
             "stock_code": stock_code,
             "customer_id": cust_id,
             "placed_on": str(datetime.now()),
             "status": "Pending",
             "stock_price": stockprice
             }
    return order


def create_match_order(buyer_id, seller_id, buyer_order_id, seller_order_id, quantity, stock_code, stock_price):
    match_order = {"trade_id": generate_id(9),
                   "buyer_id": buyer_id,
                   "seller_id": seller_id,
                   "buyer_order_id": buyer_order_id,
                   "seller_order_id": seller_order_id,
                   "quantity": quantity,
                   "stock_code": stock_code,
                   "final_price": stock_price,
                   "trade_date": str(datetime.now())}
    return match_order


def add_buy_orders(buy_orders, order):
    buy_orders.append(order)
    buy_orders = sorted(buy_orders, key=lambda i: i['stock_price'], reverse=True)
    return buy_orders


def add_sell_orders(sell_orders, order):
    sell_orders.append(order)
    sell_orders = sorted(sell_orders, key=lambda i: i['stock_price'])
    return sell_orders


def add_matched_orders(matched_orders, order):
    matched_orders.append(order)
    return matched_orders


def matching_algo(buy_orders, sell_orders, matched_orders, order,order_book):
    # order_book=[]
    if(order["trade_type"] == "Bid"):
        # Market Order Buyer
        for sell_order in sell_orders:
            if(sell_order["stock_code"] == order["stock_code"] and sell_order["quantity"] >= order["quantity"]):
                matched_order = create_match_order(order["customer_id"],
                                      sell_order["customer_id"],
                                      order["order_id"],
                                      sell_order["order_id"],
                                      order["quantity"],
                                      order["stock_code"],
                                      sell_order["stock_price"]*order["quantity"])
                order["status"] = "Completed"
                sell_order["quantity"] -= order["quantity"]
                if(sell_order["quantity"] == 0):
                    order_book[order_book.index(sell_order)]["status"] = "Completed"
                    sell_orders.remove(sell_order)
                matched_orders = add_matched_orders(matched_orders, matched_order)
                break
        if(order["status"] != "Completed"):
            buy_orders = add_buy_orders(buy_orders, order)
    else:
        # Market Order Seller
        for buy_order in buy_orders:
            if(buy_order["stock_code"] == order["stock_code"] and buy_order["quantity"] >= order["quantity"]):
                matched_order = create_match_order(buy_order["customer_id"],
                                        order["customer_id"],
                                        buy_order["order_id"],
                                        order["order_id"],
                                        order["quantity"],
                                        order["stock_code"],
                                        buy_order["stock_price"]*order["quantity"])
                order["status"] = "Completed"
                buy_order["quantity"] -= order["quantity"]
                if(buy_order["quantity"] == 0):
                    order_book[order_book.index(buy_order)]["status"] = "Completed"
                    buy_orders.remove(buy_order)
                matched_orders = add_matched_orders(matched_orders, matched_order)
                break
        if(order["status"] != "Completed"):
            sell_orders = add_sell_orders(sell_orders, order)
    order_book.append(order)
    return buy_orders, sell_orders, matched_orders,order_book


# stocks_name = ["BHARTIARTL.NS", "ASHOKLEY.NS", "AUROPHARMA.NS", "RELIANCE.NS",
#                "TCS.NS", "BAJFINANCE.NS", "HINDUNILVR.NS", "IBN", "LT.BO", "ITC.BO"]
buy_orders = []
sell_orders = []
matched_orders = []
order_book = []

def trades(request):
    order={}
    buy_orders = []
    sell_orders = []
    matched_orders = []
    order_book = []
    orders_from_db = Order.objects.all()
    for o in orders_from_db:
        order = make_order(o.id, o.order_type, o.quantity, o.stock_type, o.price)
        buy_orders, sell_orders, matched_orders,order_book = matching_algo(
            buy_orders, sell_orders, matched_orders, order, order_book)

    print(order_book)
    print("\n\n\n")
    print(matched_orders)
    context={
        'matched_orders':matched_orders,
        'order_book':order_book
    }

    return render(request,'stocks/trades.html',context)
