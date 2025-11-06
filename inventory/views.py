from django.shortcuts import render
from django.db.models import F
from .models import InventoryItem, Warehouse

def stock_list(request):
    wid = request.GET.get('warehouse')
    qs = InventoryItem.objects.select_related('warehouse', 'variant', 'variant__product')\
                              .order_by('variant__product__name', 'variant__size', 'variant__color')
    warehouses = Warehouse.objects.all()
    if wid:
        qs = qs.filter(warehouse_id=wid)

    return render(request, 'inventory/stock_list.html', {
        'stocks': qs,
        'warehouses': warehouses,
        'wid': int(wid) if wid and wid.isdigit() else None,
    })

def low_stock(request):
    qs = InventoryItem.objects.select_related('variant', 'variant__product', 'warehouse')\
          .filter(qty_on_hand__lte=F('min_qty')).order_by('variant__product__name')
    return render(request, 'inventory/low_stock.html', {'stocks': qs})
