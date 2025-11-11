from django.db import models
from django.utils.translation import gettext_lazy as _

# Пытаемся использовать ProductVariant, если он есть.
# Если нет — безопасно привязываемся к Product.
try:
    from catalog.models import ProductVariant as VariantModel  # type: ignore
    VARIANT_VERBOSE = _('Вариант')
except Exception:
    from catalog.models import Product as VariantModel  # fallback
    VARIANT_VERBOSE = _('Товар')


class Sale(models.Model):
    number = models.CharField(_('Номер чека'), max_length=32, blank=True, unique=True)
    created_at = models.DateTimeField(_('Создано'), auto_now_add=True)
    payment_method = models.CharField(
        _('Способ оплаты'),
        max_length=16,
        choices=(('cash', 'Наличные'), ('card', 'Карта')),
        default='cash',
    )
    total = models.DecimalField(_('Итого'), max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = _('Продажа')
        verbose_name_plural = _('Продажи')
        ordering = ['-created_at']

    def __str__(self):
        return f'#{self.number or self.pk} от {self.created_at:%Y-%m-%d %H:%M}'


class SaleItem(models.Model):
    sale = models.ForeignKey(
        Sale, on_delete=models.CASCADE, related_name='items', verbose_name=_('Чек')
    )

    # ВАЖНО: теперь FK указывает на VariantModel (ProductVariant ИЛИ Product)
    variant = models.ForeignKey(
        VariantModel,
        on_delete=models.PROTECT,
        related_name='sale_items',
        null=True,
        blank=True,
        verbose_name=VARIANT_VERBOSE,
    )

    name = models.CharField(_('Название позиции'), max_length=255, blank=True)
    sku = models.CharField(_('SKU / Штрихкод'), max_length=64, blank=True)
    price = models.DecimalField(_('Цена'), max_digits=10, decimal_places=2, default=0)
    qty = models.PositiveIntegerField(_('Кол-во'), default=1)
    subtotal = models.DecimalField(_('Сумма'), max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = _('Позиция чека')
        verbose_name_plural = _('Позиции чека')

    def __str__(self):
        return self.name or f'{self.variant} x{self.qty}'

    def save(self, *args, **kwargs):
        # Автозаполнение name/sku из варианта/товара при необходимости
        if self.variant:
            if not self.name:
                # у варианта может быть .name, а может не быть — тогда берём у product/name
                self.name = getattr(self.variant, 'name', '') or getattr(
                    getattr(self.variant, 'product', None), 'name', ''
                )
            if not self.sku:
                self.sku = getattr(self.variant, 'sku', '') or ''
        # пересчёт суммы
        self.subtotal = (self.price or 0) * (self.qty or 0)
        super().save(*args, **kwargs)
