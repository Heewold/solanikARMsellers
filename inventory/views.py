# inventory/views.py
from django.shortcuts import render
from django.db.models import F, Q
from .models import InventoryItem  # только модели!

def _base_qs():
    # Подтягиваем связанные сущности, чтобы в шаблоне было удобно показывать данные
    return (InventoryItem.objects
            .select_related("variant", "variant__product", "warehouse"))

def stock_list(request):
    """
    Общий список остатков.
    """
    items = _base_qs().order_by("id")
    ctx = {
        "page_name": "stock",
        "items": items,
    }
    return render(request, "inventory/stock_list.html", ctx)

def stock_low(request):
    """
    Низкие остатки. Если в модели есть поле min_qty — фильтруем по нему,
    иначе считаем «низким» <= 5 штук.
    """
    qs = _base_qs()
    if hasattr(InventoryItem, "min_qty"):
        items = qs.filter(qty__lte=F("min_qty"))
    else:
        items = qs.filter(qty__lte=5)

    ctx = {
        "page_name": "stock_low",
        "items": items.order_by("id"),
    }
    return render(request, "inventory/stock_low.html", ctx)
