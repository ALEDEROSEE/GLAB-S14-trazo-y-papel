from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from .models import MovimientoInventario, Producto


@transaction.atomic
def registrar_movimiento(*, producto, tipo, cantidad, motivo, usuario):
    if not usuario.is_active or not usuario.has_perm('catalogo.change_producto'):
        raise ValidationError('No tienes permiso para modificar el inventario.')
    if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad < 1:
        raise ValidationError('La cantidad debe ser un entero mayor que cero.')
    if tipo not in MovimientoInventario.Tipo.values:
        raise ValidationError('Selecciona una entrada o una salida.')
    motivo = motivo.strip()
    if not motivo or len(motivo) > 160:
        raise ValidationError('Escribe un motivo de entre 1 y 160 caracteres.')
    delta = cantidad if tipo == MovimientoInventario.Tipo.ENTRADA else -cantidad
    productos = Producto.objects.filter(pk=producto.pk)
    if delta < 0:
        productos = productos.filter(cantidad_disponible__gte=cantidad)
    # La condición y la resta se ejecutan juntas en la base de datos.
    if not productos.update(cantidad_disponible=F('cantidad_disponible') + delta):
        raise ValidationError('Stock insuficiente. No se registró la salida.')
    producto.refresh_from_db(fields=['cantidad_disponible'])
    return MovimientoInventario.objects.create(
        producto=producto, tipo=tipo, cantidad=cantidad, motivo=motivo,
        stock_anterior=producto.cantidad_disponible - delta,
        stock_posterior=producto.cantidad_disponible, usuario=usuario,
    )
