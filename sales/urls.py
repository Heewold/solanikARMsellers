# sales/urls.py
from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.pos, name='pos'),
    path('history/', views.sales_history, name='sales_history'),
    path('checkout/', views.pos_checkout, name='pos_checkout'),
    path('search/', views.search, name='search'),  # можно удалить, если не используешь
]
