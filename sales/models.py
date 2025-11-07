from django.db import models
from django.contrib.auth import get_user_model
from catalog.models import ProductVariant
from inventory.models import Warehouse

User = get_user_model()


class Sale(models.Model):
    """Продажа / чек"""
    created_at = models.DateTimeField("Дата и время", auto_now_add=True)
    user = models.ForeignKey(User, verbose_name="Продавец", on_delete=models.PROTECT)
    warehouse = models.ForeignKey(Warehouse, verbose_name="Склад", on_delete=models.PROTECT)
    total_amount = models.DecimalField("Сумма чека", max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField("Скидка", max_digits=12, decimal_places=2, default=0)
    final_amount = models.DecimalField("Итоговая сумма", max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Продажа"
        verbose_name_plural = "Продажи"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Чек #{self.id} от {self.created_at.strftime('%d.%m.%Y %H:%M')}"

    def recalc_totals(self):
        total = sum(item.subtotal for item in self.items.all())
        self.total_amount = total
        self.final_amount = total - self.discount_amount
        self.save(update_fields=["total_amount", "final_amount"])


class SaleItem(models.Model):
    """Строка продажи (товар в чеке)"""
    sale = models.ForeignKey(Sale, verbose_name="Продажа", on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, verbose_name="Вариант товара", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField("Количество", default=1)
    price = models.DecimalField("Цена", max_digits=12, decimal_places=2)
    subtotal = models.DecimalField("Сумма", max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "Позиция продажи"
        verbose_name_plural = "Позиции продаж"

    def __str__(self):
        return f"{self.variant} x {self.quantity}"

    def save(self, *args, **kwargs):
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)
        self.sale.recalc_totals()
