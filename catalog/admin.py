from django.contrib import admin
from django.utils.html import format_html

from .models import Product, ProductImage, Brand, Category


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('id', 'name')
    ordering = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('id', 'name', 'parent')
    list_filter = ('parent',)
    ordering = ('name',)


class ProductImageInline(admin.TabularInline):  # можно StackedInline, если хочется повыше форму
    model = ProductImage
    extra = 1
    fields = ('preview', 'image', 'is_main')
    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="height:64px; border-radius:6px; box-shadow:0 0 0 1px rgba(0,0,0,.06)" />',
                obj.image.url
            )
        return '—'
    preview.short_description = 'Превью'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'brand', 'category')
    search_fields = ('name', 'brand__name', 'category__name')
    list_filter = ('brand', 'category')
    inlines = [ProductImageInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'is_main', 'thumb')
    list_filter = ('is_main', 'product__brand', 'product__category')
    search_fields = ('product__name',)

    def thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:48px;border-radius:4px" />', obj.image.url)
        return '—'
    thumb.short_description = 'Превью'
