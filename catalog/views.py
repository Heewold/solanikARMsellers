from django.shortcuts import render
from .models import Product, Brand, Category

def product_list(request):
    q = request.GET.get("q", "").strip()
    brand_id = request.GET.get("brand")
    category_id = request.GET.get("category")

    qs = Product.objects.select_related("brand", "category").prefetch_related("variants")

    if q:
        qs = (
            qs.filter(name__icontains=q)
            | qs.filter(variants__sku__icontains=q)
            | qs.filter(variants__barcode__icontains=q)
        ).distinct()

    if brand_id:
        qs = qs.filter(brand_id=brand_id)
    if category_id:
        qs = qs.filter(category_id=category_id)

    context = {
        "products": qs.order_by("name")[:200],
        "brands": Brand.objects.all().order_by("name"),
        "categories": Category.objects.filter(parent__isnull=True).order_by("name"),
        "q": q,
        "brand_selected": int(brand_id) if brand_id and brand_id.isdigit() else None,
        "category_selected": int(category_id) if category_id and category_id.isdigit() else None,
    }
    return render(request, "catalog/product_list.html", context)
