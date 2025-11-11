# arm_seller_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include(('catalog.urls', 'catalog'), namespace='catalog')),

    # Касса / История продаж
    path('pos/', include(('sales.urls', 'sales'), namespace='sales')),

    # Склад
    path('stock/', include(('inventory.urls', 'inventory'), namespace='inventory')),

    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)