from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render
from django.views.decorators.http import require_POST

from catalog.models import Product, ProductVariant
from inventory.models import Warehouse, StockMovement, InventoryItem
from .models import Sale, SaleItem


# --------- Константа ключа корзины в сессии ---------
CART_KEY = "pos_cart"


# --------- Helpers ---------
def _get_cart(session):
    """Получить корзину из сессии."""
    return session.get(CART_KEY, {"items": []})


def _save_cart(session, cart):
    """Сохранить корзину в сессию."""
    session[CART_KEY] = cart
    session.modified = True


def _cart_total(cart):
    """Посчитать сумму корзины."""
    total = Decimal("0")
    for it in cart["items"]:
        total += Decimal(str(it["price"])) * it["qty"]
    return total


def _render_cart(request):
    """Вернуть частичный шаблон корзины."""
    cart = _get_cart(request.session)
    return render(request, "sales/_cart.html", {"cart": cart, "total": _cart_total(cart)})


# --------- Страницы / partials ---------
@login_required
def pos_home(request):
    return render(request, "sales/pos.html")


@login_required
def pos_cart(request):
    return _render_cart(request)


@login_required
def pos_search(request):
    """Поиск по SKU/штрихкоду/названию (GET)."""
    q = (request.GET.get("q") or "").strip()
    ctx = {"q": q, "results": []}
    if not q:
        return render(request, "sales/_search_results.html", ctx)

    # 1) точный SKU
    variants = ProductVariant.objects.select_related("product").filter(sku__iexact=q)

    # 2) точный штрихкод
    if not variants.exists():
        variants = ProductVariant.objects.select_related("product").filter(barcode__iexact=q)

    # 3) по названию товара (топ-20) → их варианты
    if not variants.exists():
        products = Product.objects.filter(name__icontains=q)[:20]
        variants = ProductVariant.objects.select_related("product").filter(product__in=products)

    ctx["results"] = variants[:50]
    return render(request, "sales/_search_results.html", ctx)


# --------- Операции с корзиной (всегда возвращают HTML корзины) ---------
@login_required
@require_POST
def pos_add(request):
    try:
        variant_id = int(request.POST.get("variant_id"))
    except (TypeError, ValueError):
        # вернём корзину как есть
        return _render_cart(request)

    variant = ProductVariant.objects.select_related("product").get(id=variant_id)
    price = variant.price_effective

    cart = _get_cart(request.session)

    # если уже есть — инкремент
    for it in cart["items"]:
        if it["variant_id"] == variant.id:
            it["qty"] += 1
            _save_cart(request.session, cart)
            return _render_cart(request)

    # иначе добавляем новую позицию
    cart["items"].append({
        "variant_id": variant.id,
        "name": variant.product.name,
        "sku": variant.sku,
        "size": variant.size,
        "color": variant.color,
        "price": float(price),
        "qty": 1,
    })
    _save_cart(request.session, cart)
    return _render_cart(request)


@login_required
@require_POST
def pos_inc(request):
    vid = int(request.POST.get("id"))
    cart = _get_cart(request.session)
    for it in cart["items"]:
        if it["variant_id"] == vid:
            it["qty"] += 1
            break
    _save_cart(request.session, cart)
    return _render_cart(request)


@login_required
@require_POST
def pos_dec(request):
    vid = int(request.POST.get("id"))
    cart = _get_cart(request.session)
    for it in cart["items"]:
        if it["variant_id"] == vid:
            it["qty"] = max(1, it["qty"] - 1)
            break
    _save_cart(request.session, cart)
    return _render_cart(request)


@login_required
@require_POST
def pos_remove(request):
    vid = int(request.POST.get("id"))
    cart = _get_cart(request.session)
    cart["items"] = [it for it in cart["items"] if it["variant_id"] != vid]
    _save_cart(request.session, cart)
    return _render_cart(request)


@login_required
@require_POST
def pos_clear(request):
    _save_cart(request.session, {"items": []})
    return _render_cart(request)


# --------- Оформление продажи ---------
@login_required
@require_POST
@transaction.atomic
def pos_checkout(request):
    """
    Оформление чека:
    - проверяем корзину и склад
    - валидируем доступные остатки
    - создаём Sale, SaleItem
    - создаём движения OUT
    - чистим корзину
    - возвращаем модалку успеха
    Если что-то не так — рендерим _checkout_error.html (в модалку).
    """
    cart = _get_cart(request.session)

    # Пустая корзина
    if not cart.get("items"):
        return render(
            request, "sales/_checkout_error.html",
            {"shortages": [], "warehouse": None, "error_message": "Корзина пуста"},
            status=400,
        )

    # Склад
    wh = Warehouse.objects.filter(is_default=True).first() or Warehouse.objects.first()
    if not wh:
        return render(
            request, "sales/_checkout_error.html",
            {"shortages": [], "warehouse": None, "error_message": "Нет склада"},
            status=400,
        )

    # Проверка остатков
    shortages = []
    variants_cache = {}
    for it in cart["items"]:
        vid = int(it["variant_id"])
        if vid not in variants_cache:
            variants_cache[vid] = ProductVariant.objects.select_related("product").get(id=vid)
        variant = variants_cache[vid]
        qty = int(it["qty"])

        stock = InventoryItem.objects.filter(warehouse=wh, variant=variant).first()
        available = (stock.qty_on_hand - stock.qty_reserved) if stock else 0
        if available < qty:
            shortages.append({"variant": variant, "need": qty, "available": available})

    if shortages:
        return render(
            request, "sales/_checkout_error.html",
            {"shortages": shortages, "warehouse": wh},
            status=400,
        )

    # Всё ок — создаём чек и позиции; списываем остатки движениями OUT
    sale = Sale.objects.create(user=request.user, warehouse=wh)

    for it in cart["items"]:
        variant = variants_cache[int(it["variant_id"])]
        qty = int(it["qty"])
        price = Decimal(str(it["price"]))

        SaleItem.objects.create(
            sale=sale,
            variant=variant,
            quantity=qty,
            price=price,
        )

        StockMovement.objects.create(
            warehouse=wh,
            variant=variant,
            move_type="OUT",
            qty_delta=-qty,
            note=f"Продажа #{sale.id}",
        )

    sale.recalc_totals()

    # Очистка корзины
    _save_cart(request.session, {"items": []})

    return render(request, "sales/_checkout_success.html", {"sale": sale})

from django.shortcuts import render, get_object_or_404  # ← добавь импорт

from django.contrib.auth.decorators import login_required
from .models import Sale

@login_required
def sales_history(request):
    """Список последних продаж."""
    qs = (
        Sale.objects
        .select_related("user", "warehouse")
        .order_by("-created_at")[:200]
    )
    return render(request, "sales/history.html", {"sales": qs})

@login_required
def sale_receipt(request, sale_id: int):
    """Страница/печать конкретного чека."""
    sale = get_object_or_404(
        Sale.objects.prefetch_related("items__variant__product"),
        id=sale_id
    )
    return render(request, "sales/receipt.html", {"sale": sale})
