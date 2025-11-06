from django.contrib import admin
from .models import Warehouse, InventoryItem, StockMovement

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_default')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('variant', 'warehouse', 'qty_on_hand', 'qty_reserved', 'min_qty', 'available')
    list_filter = ('warehouse', 'variant__product__brand', 'variant__product__category')
    search_fields = ('variant__product__name', 'variant__sku', 'variant__color')
    autocomplete_fields = ('variant', 'warehouse')  # оставляем

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'move_type', 'variant', 'warehouse', 'qty_delta', 'user', 'note')
    list_filter = ('move_type', 'warehouse')
    date_hierarchy = 'created_at'
    search_fields = ('variant__sku', 'variant__product__name', 'note')
    autocomplete_fields = ('variant', 'warehouse')

