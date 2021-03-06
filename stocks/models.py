from django.db import models
# from django.utils import timezone
from datetime import datetime

# Create your models here.

choices=(
    ("Bid", "Bid"),
    ("Ask","Ask")
)

stock_choices=(
    ("BHARTIARTL.NS","BHARTIARTL.NS"), 
    ("ASHOKLEY.NS", "ASHOKLEY.NS"),
    ("AUROPHARMA.NS", "AUROPHARMA.NS"),
    ("RELIANCE.NS","RELIANCE.NS"),
    ("TCS.NS", "TCS.NS"),
    ("BAJFINANCE.NS", "BAJFINANCE.NS"),
    ("HINDUNILVR.NS", "HINDUNILVR.NS"),
    ("IBN","IBN"), 
    ("LT.BO", "LT.BO"),
    ("ITC.BO", "ITC.BO")
)

class Order(models.Model):
    id=models.CharField(max_length=15,primary_key=True)
    stock_type = models.CharField(max_length=255, default="", choices=stock_choices)
    price=models.FloatField(default=0)
    quantity=models.IntegerField(default=0)
    order_type=models.CharField(max_length=255, choices=choices)
    placed_on = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.id
