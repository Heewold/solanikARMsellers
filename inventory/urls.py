# inventory/urls.py
from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.stock_list, name="stock_list"),          # /stock/
    path("low/", views.stock_low, name="stock_low"),        # /stock/low/
]
