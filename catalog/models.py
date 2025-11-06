from django.db import models


class Brand(models.Model):
    name = models.CharField('Название', max_length=120, unique=True)
    slug = models.SlugField('Слаг', max_length=140, unique=True)

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    name = models.CharField('Название', max_length=120)
    slug = models.SlugField('Слаг', max_length=140)
    parent = models.ForeignKey(
        'self',
        verbose_name='Родительская категория',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        unique_together = ('slug', 'parent')
        ordering = ['name']

    def __str__(self) -> str:
        return f'{self.parent} / {self.name}' if self.parent else self.name


class Product(models.Model):
    class Gender(models.TextChoices):
        UNISEX = 'UNISEX', 'Унисекс'
        MEN = 'MEN', 'Мужское'
        WOMEN = 'WOMEN', 'Женское'
        KIDS = 'KIDS', 'Детское'

    class Season(models.TextChoices):
        ALL = 'ALL', 'Круглый год'
        SS = 'SS', 'Весна/Лето'
        FW = 'FW', 'Осень/Зима'

    name = models.CharField('Название', max_length=255, db_index=True)
    brand = models.ForeignKey(
        Brand, verbose_name='Бренд', on_delete=models.PROTECT, related_name='products'
    )
    category = models.ForeignKey(
        Category, verbose_name='Категория', on_delete=models.PROTECT, related_name='products'
    )

    gender = models.CharField('Пол', max_length=10, choices=Gender.choices, default=Gender.UNISEX)
    season = models.CharField('Сезон', max_length=10, choices=Season.choices, default=Season.ALL)
    material = models.CharField('Материал', max_length=120, blank=True, help_text='Напр.: 100% хлопок')

    price = models.DecimalField('Цена, ₽', max_digits=12, decimal_places=2)
    cost = models.DecimalField('Себестоимость, ₽', max_digits=12, decimal_places=2, default=0)
    vat_rate = models.DecimalField('Ставка НДС, %', max_digits=4, decimal_places=2, default=20)

    description = models.TextField('Описание', blank=True)
    is_active = models.BooleanField('Активен', default=True)

    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлён', auto_now=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class ProductVariant(models.Model):
    """
    Вариант одежды: комбинация размера и цвета.
    Может иметь собственный SKU/штрих-код и переопределённую цену.
    """
    product = models.ForeignKey(
        Product, verbose_name='Товар', on_delete=models.CASCADE, related_name='variants'
    )

    class Size(models.TextChoices):
        XXS = 'XXS', 'XXS'
        XS = 'XS', 'XS'
        S = 'S', 'S'
        M = 'M', 'M'
        L = 'L', 'L'
        XL = 'XL', 'XL'
        XXL = 'XXL', 'XXL'
        XXXL = 'XXXL', '3XL'

    size = models.CharField('Размер', max_length=6, choices=Size.choices)
    color = models.CharField('Цвет', max_length=50, help_text='Напр.: Black, White, Navy')

    sku = models.CharField('SKU', max_length=64, unique=True)
    barcode = models.CharField('Штрих-код', max_length=64, blank=True, null=True, unique=True)

    price_override = models.DecimalField(
        'Цена варианта, ₽', max_digits=12, decimal_places=2, null=True, blank=True,
        help_text='Если пусто — берётся цена товара'
    )

    class Meta:
        verbose_name = 'Вариант товара'
        verbose_name_plural = 'Варианты товара'
        unique_together = ('product', 'size', 'color')
        ordering = ['product__name', 'size', 'color']

    def __str__(self) -> str:
        return f'{self.product.name} — {self.size} / {self.color}'

    @property
    def price_effective(self):
        """Фактическая цена с учётом переопределения на варианте."""
        return self.price_override if self.price_override is not None else self.product.price


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, verbose_name='Товар', on_delete=models.CASCADE, related_name='images'
    )
    image = models.ImageField('Изображение', upload_to='products/')
    is_primary = models.BooleanField('Основное фото', default=False)

    class Meta:
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'

    def __str__(self) -> str:
        return f'Фото {self.product.name}'
