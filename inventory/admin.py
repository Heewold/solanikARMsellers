# inventory/admin.py
from django.contrib import admin
from .models import InventoryItem, StockMovement


class SafeColumnsMixin:
    """Набор безопасных геттеров для колонок в админке."""
    def _get(self, obj, *names, default="-"):
        for n in names:
            if hasattr(obj, n):
                try:
                    val = getattr(obj, n)
                    return val() if callable(val) else val
                except Exception:
                    pass
        return default


@admin.register(InventoryItem)
class InventoryItemAdmin(SafeColumnsMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "product_col",
        "warehouse_col",
        "qty_on_hand_col",
        "qty_reserved_col",
        "min_qty_col",
        "available_col",
    )
    list_select_related = True

    list_filter = (
        ("product__brand", admin.RelatedOnlyFieldListFilter),
        ("product__category", admin.RelatedOnlyFieldListFilter),
        ("warehouse", admin.RelatedOnlyFieldListFilter),
    )

    search_fields = (
        "product__name",
        "product__sku",
        "warehouse__name",
    )

    # ---- безопасные колонки ----
    def product_col(self, obj):
        # product/name — нагляднее в списке
        p = self._get(obj, "product", default=None)
        return getattr(p, "name", str(p)) if p else "-"
    product_col.short_description = "Товар"

    def warehouse_col(self, obj):
        return self._get(obj, "warehouse", default="-")
    warehouse_col.short_description = "Склад"

    def qty_on_hand_col(self, obj):
        # пробуем разные варианты названий в модели
        return self._get(obj, "qty_on_hand", "on_hand", "stock", default=0)
    qty_on_hand_col.short_description = "На складе"

    def qty_reserved_col(self, obj):
        return self._get(obj, "qty_reserved", "reserved", default=0)
    qty_reserved_col.short_description = "Резерв"

    def min_qty_col(self, obj):
        return self._get(obj, "min_qty", "min_stock", default=0)
    min_qty_col.short_description = "Мин. остаток"

    def available_col(self, obj):
        # иногда это поле/свойство называется по-разному
        return self._get(obj, "available", "available_qty", default=0)
    available_col.short_description = "Доступно"


@admin.register(StockMovement)
class StockMovementAdmin(SafeColumnsMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "product_col",
        "warehouse_col",
        "movement_type_col",   # виртуальная колонка
        "qty_col",
        "created_at_col",
    )
    list_select_related = True
    date_hierarchy = "created_at"

    # ВАЖНО: убрали проблемный 'movement_type' из фильтров
    list_filter = (
        ("warehouse", admin.RelatedOnlyFieldListFilter),
        ("product__brand", admin.RelatedOnlyFieldListFilter),
        ("product__category", admin.RelatedOnlyFieldListFilter),
        "created_at",
    )

    search_fields = (
        "product__name",
        "product__sku",
        "warehouse__name",
        "comment",
    )

    # ---- безопасные колонки ----
    def product_col(self, obj):
        return self._get(obj, "product", default="-")
    product_col.short_description = "Товар"

    def warehouse_col(self, obj):
        return self._get(obj, "warehouse", default="-")
    warehouse_col.short_description = "Склад"

    def movement_type_col(self, obj):
        # Если в модели есть поле type/kind/direction — покажем его
        return self._get(obj, "movement_type", "type", "kind", "direction", default="-")
    movement_type_col.short_description = "Тип"

    def qty_col(self, obj):
        return self._get(obj, "qty", "quantity", default=0)
    qty_col.short_description = "Кол-во"

    def created_at_col(self, obj):
        return self._get(obj, "created_at", default="-")
    created_at_col.short_description = "Создано"
    created_at_col.admin_order_field = "created_at"
