from django.db import models
from django.utils.translation import gettext_lazy as _

# Аккуратно пытаемся подхватить ProductVariant. Если его нет – используем Product.
try:
    from catalog.models import ProductVariant as VariantModel  # type: ignore
    VARIANT_VERBOSE = _('Вариант')
except Exception:
    from catalog.models import Product as VariantModel  # fallback
    VARIANT_VERBOSE = _('Товар')


class Warehouse(models.Model):
    name = models.CharField(_('Название склада'), max_length=120, unique=True)
    slug = models.SlugField(_('Слаг'), max_length=64, unique=True)
    is_default = models.BooleanField(_('По умолчанию'), default=False)

    class Meta:
        verbose_name = _('Склад')
        verbose_name_plural = _('Склады')
        ordering = ['name']

    def __str__(self):
        return self.name


class InventoryItem(models.Model):
    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, related_name='items', verbose_name=_('Склад')
    )
    # ВАЖНО: поле называется "variant", но тип — тот, что мы импортировали выше
    variant = models.ForeignKey(
        VariantModel, on_delete=models.CASCADE, related_name='stock', verbose_name=VARIANT_VERBOSE
    )
    qty = models.IntegerField(_('Остаток'), default=0)

    class Meta:
        verbose_name = _('Остаток на складе')
        verbose_name_plural = _('Остатки на складе')
        unique_together = (('warehouse', 'variant'),)
        ordering = ['warehouse_id']

    def __str__(self):
        return f'{self.warehouse} — {self.variant} : {self.qty}'


class StockMovement(models.Model):
    class MoveType(models.TextChoices):
        IN = 'IN', _('Приход')
        OUT = 'OUT', _('Расход')

    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, related_name='movements', verbose_name=_('Склад')
    )
    variant = models.ForeignKey(
        VariantModel, on_delete=models.CASCADE, related_name='movements', verbose_name=VARIANT_VERBOSE
    )
    move_type = models.CharField(_('Тип движения'), max_length=3, choices=MoveType.choices)
    qty_delta = models.IntegerField(_('Кол-во'), default=0)
    note = models.CharField(_('Примечание'), max_length=255, blank=True)
    created_at = models.DateTimeField(_('Когда'), auto_now_add=True)

    class Meta:
        verbose_name = _('Движение товара')
        verbose_name_plural = _('Движения товара')
        ordering = ['-created_at']

    def __str__(self):
        sign = '+' if self.move_type == self.MoveType.IN else '−'
        return f'{self.created_at:%Y-%m-%d %H:%M} {self.warehouse} {sign}{abs(self.qty_delta)} {self.variant}'
