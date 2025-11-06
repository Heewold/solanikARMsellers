from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from catalog.models import ProductVariant, Product

User = get_user_model()


class Warehouse(models.Model):
    name = models.CharField('Склад', max_length=120, unique=True)
    slug = models.SlugField('Слаг', max_length=140, unique=True)
    is_default = models.BooleanField('Склад по умолчанию', default=True)

    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склады'
        ordering = ['name']

    def __str__(self):
        return self.name


class InventoryItem(models.Model):
    """Остаток конкретного варианта на складе."""
    warehouse = models.ForeignKey(Warehouse, verbose_name='Склад',
                                  on_delete=models.CASCADE, related_name='stocks')
    variant = models.ForeignKey(ProductVariant, verbose_name='Вариант',
                                on_delete=models.CASCADE, related_name='stocks')

    qty_on_hand = models.IntegerField('На руках', default=0)
    qty_reserved = models.IntegerField('Резерв', default=0)
    min_qty = models.IntegerField('Мин. остаток', default=0)

    class Meta:
        verbose_name = 'Остаток'
        verbose_name_plural = 'Остатки'
        unique_together = ('warehouse', 'variant')

    def __str__(self):
        return f'{self.variant} @ {self.warehouse} = {self.qty_on_hand}'

    @property
    def available(self) -> int:
        return self.qty_on_hand - self.qty_reserved

    @property
    def product(self) -> Product:
        return self.variant.product


class StockMovement(models.Model):
    class Type(models.TextChoices):
        IN = 'IN', 'Приход'
        OUT = 'OUT', 'Расход'
        ADJUST = 'ADJ', 'Корректировка'

    created_at = models.DateTimeField('Создано', default=timezone.now)
    user = models.ForeignKey(User, verbose_name='Пользователь',
                             on_delete=models.SET_NULL, null=True, blank=True)

    warehouse = models.ForeignKey(Warehouse, verbose_name='Склад',
                                  on_delete=models.PROTECT, related_name='moves')
    variant = models.ForeignKey(ProductVariant, verbose_name='Вариант',
                                on_delete=models.PROTECT, related_name='moves')

    move_type = models.CharField('Тип', max_length=4, choices=Type.choices)
    qty_delta = models.IntegerField('Δ Количество')  # + для прихода, – для расхода
    note = models.CharField('Комментарий', max_length=255, blank=True)

    class Meta:
        verbose_name = 'Движение'
        verbose_name_plural = 'Движения'
        ordering = ['-created_at']

    def __str__(self):
        sign = '+' if self.qty_delta >= 0 else ''
        return f'[{self.get_move_type_display()}] {self.variant} {sign}{self.qty_delta}'

    def apply(self):
        """Атомично применяет движение к остаткам."""
        with transaction.atomic():
            stock, _ = InventoryItem.objects.select_for_update().get_or_create(
                warehouse=self.warehouse, variant=self.variant
            )
            new_qty = stock.qty_on_hand + self.qty_delta
            if new_qty < 0:
                raise ValueError('Нельзя списать больше, чем есть на складе')
            stock.qty_on_hand = new_qty
            stock.save()

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            # применять только при первом сохранении, чтобы не удваивать эффект
            self.apply()
