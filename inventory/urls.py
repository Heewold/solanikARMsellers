from django.urls import path
from .views import stock_list, low_stock

urlpatterns = [
    path('', stock_list, name='stock_list'),
    path('low/', low_stock, name='low_stock'),
]
