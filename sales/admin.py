# sales/admin.py
from django.contrib import admin
from .models import Sale, SaleItem


def _get(obj, *names, default="-"):
    for n in names:
        if hasattr(obj, n):
            try:
                val = getattr(obj, n)
                return val() if callable(val) else val
            except Exception:
                pass
    return default


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    """
    Убираем несуществующие 'seller' и 'items_count'.
    Делаем безопасную колонку counts через related_name items (или объектный менеджер).
    """
    list_display = (
        "id",
        "created_at_col",
        "total_col",
        "payment_col",
        "items_count_col",
    )
    date_hierarchy = "created_at"

    list_filter = (
        "created_at",
        "payment_method",  # если есть
    )

    search_fields = (
        "id",
        "customer__name",  # если есть
    )

    def created_at_col(self, obj):
        return _get(obj, "created_at")
    created_at_col.short_description = "Дата"

    def total_col(self, obj):
        return _get(obj, "total", "amount", "total_amount", default=0)
    total_col.short_description = "Сумма"

    def payment_col(self, obj):
        return _get(obj, "payment_method", default="-")
    payment_col.short_description = "Оплата"

    def items_count_col(self, obj):
        """
        Попытка посчитать количество позиций.
        Пытаемся через related 'items', потом 'saleitem_set'.
        """
        try:
            if hasattr(obj, "items"):
                return obj.items.count()
            # fallback по умолчанию
            return obj.saleitem_set.count()
        except Exception:
            return 0

    items_count_col.short_description = "Позиций"


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "sale",
        "product_col",
        "qty_col",
        "price_col",
        "total_col",
    )
    list_select_related = True

    search_fields = (
        "sale__id",
        "product__name",
        "product__sku",
    )

    def product_col(self, obj):
        return _get(obj, "product")
    product_col.short_description = "Товар"

    def qty_col(self, obj):
        return _get(obj, "qty", "quantity", default=0)
    qty_col.short_description = "Кол-во"

    def price_col(self, obj):
        return _get(obj, "price", "unit_price", default=0)
    price_col.short_description = "Цена"

    def total_col(self, obj):
        # total или qty*price
        val = _get(obj, "total", default=None)
        if val not in (None, "-"):
            return val
        try:
            q = self.qty_col(obj) or 0
            p = self.price_col(obj) or 0
            if isinstance(q, (int, float)) and isinstance(p, (int, float)):
                return q * p
        except Exception:
            pass
        return 0
    total_col.short_description = "Сумма"
