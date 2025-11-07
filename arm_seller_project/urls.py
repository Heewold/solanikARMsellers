from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('products/', include('catalog.urls')),  # список товаров
    path('stock/', include('inventory.urls')),
    path("pos/", include("sales.urls")),
]
