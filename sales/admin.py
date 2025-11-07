from django.contrib import admin
from .models import Sale, SaleItem

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "user", "warehouse", "final_amount")
    list_filter = ("warehouse", "user")
    date_hierarchy = "created_at"
    inlines = [SaleItemInline]
