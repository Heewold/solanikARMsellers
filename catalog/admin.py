from django.contrib import admin
from .models import Brand, Category, Product, ProductVariant, ProductImage

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "slug")
    list_filter = ("parent",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ("size", "color", "sku", "barcode", "price_override")

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "category", "price", "is_active")
    list_filter = ("brand", "category", "gender", "season", "is_active")
    search_fields = ("name", "variants__sku", "variants__barcode")
    inlines = [ProductImageInline, ProductVariantInline]

from django.contrib import admin

admin.site.site_header = "АРМ Продавца — администрирование"
admin.site.site_title  = "АРМ Продавца"
admin.site.index_title = "Панель управления"