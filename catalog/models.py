from django.db import models
from django.core.exceptions import ValidationError


class Brand(models.Model):
    name = models.CharField('Бренд', max_length=120, unique=True)

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    name = models.CharField('Категория', max_length=120, unique=True)
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    name = models.CharField('Название', max_length=255)
    brand = models.ForeignKey(Brand, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Бренд')
    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Категория'
    )
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name

    @property
    def main_image(self):
        """
        Удобный доступ к главной картинке: вернёт изображение, помеченное как is_main,
        иначе — первое по порядку; иначе — None.
        """
        img = self.images.filter(is_main=True).first()
        if img:
            return img
        return self.images.first()


def product_image_upload_to(instance: 'ProductImage', filename: str) -> str:
    # Путь хранения: media/products/<год>/<месяц>/<имя файла>
    return f'products/{instance.created_at:%Y}/{instance.created_at:%m}/{filename}'


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='images', verbose_name='Товар'
    )
    image = models.ImageField('Фото', upload_to=product_image_upload_to)
    is_main = models.BooleanField('Основное', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Фото товара'
        verbose_name_plural = 'Фото товара'
        ordering = ['-is_main', 'id']

    def __str__(self) -> str:
        return f'{self.product} — {self.image.name if self.image else "без файла"}'

    def clean(self):
        # Разрешаем только одну «главную» фотографию на товар
        if self.is_main:
            qs = ProductImage.objects.filter(product=self.product, is_main=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError('У этого товара уже есть основная фотография.')

    def save(self, *args, **kwargs):
        # Валидация при сохранении через админку/ORM
        self.full_clean()
        return super().save(*args, **kwargs)
