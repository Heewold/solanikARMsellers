# catalog/views.py
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render
from catalog.models import Product   # <-- добавьте этот импорт

def product_list(request):
    products = (
        Product.objects
        .select_related('brand', 'category')
        .prefetch_related('images')
    )
    return render(request, 'catalog/product_list.html', {
        'products': products,
        'page_name': 'products',
    })


def product_detail(request, pk: int):
    product = get_object_or_404(
        Product.objects.select_related("brand")
        .prefetch_related(Prefetch("images", queryset=ProductImage.objects.order_by("-is_main", "id")),
                          "variants"),
        pk=pk,
    )
    return render(request, "catalog/product_detail.html", {"product": product})
