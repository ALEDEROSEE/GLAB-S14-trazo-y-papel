from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ['nombre']
        verbose_name_plural = 'categorías'

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=9, decimal_places=2, validators=[MinValueValidator(0)])
    imagen = models.CharField(max_length=500, blank=True, help_text='URL o ruta de imagen')
    cantidad_disponible = models.PositiveIntegerField(default=0)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    descuento_porcentaje = models.PositiveSmallIntegerField(
        default=0, validators=[MaxValueValidator(80)],
        help_text='Descuento de 0 a 80 %. El precio original se conserva.'
    )

    @property
    def precio_final(self):
        factor = (Decimal(100) - self.descuento_porcentaje) / Decimal(100)
        return (self.precio * factor).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class MovimientoInventario(models.Model):
    class Tipo(models.TextChoices):
        ENTRADA = 'entrada', 'Entrada'
        SALIDA = 'salida', 'Salida'

    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='movimientos')
    tipo = models.CharField(max_length=7, choices=Tipo.choices)
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    motivo = models.CharField(max_length=160)
    stock_anterior = models.PositiveIntegerField()
    stock_posterior = models.PositiveIntegerField()
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado', '-id']
        verbose_name = 'movimiento de inventario'
        verbose_name_plural = 'movimientos de inventario'

    def __str__(self):
        return f'{self.get_tipo_display()} de {self.cantidad} — {self.producto}'
