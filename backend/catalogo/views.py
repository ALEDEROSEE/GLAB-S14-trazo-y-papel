from rest_framework import generics
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Case, When, Value, IntegerField
from .models import Categoria, Producto
from .serializers import CategoriaSerializer, ProductoSerializer


class CategoriaList(generics.ListAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class ProductoList(generics.ListAPIView):
    serializer_class = ProductoSerializer

    def get_queryset(self):
        productos = Producto.objects.select_related('categoria')
        params = self.request.query_params
        buscar = params.get('buscar', '').strip()[:100]
        if buscar:
            productos = productos.filter(Q(nombre__icontains=buscar) | Q(descripcion__icontains=buscar))
        categoria = params.get('categoria', '')
        if categoria:
            if not categoria.isascii() or not categoria.isdecimal() or len(categoria) > 18:
                raise ValidationError({'categoria': 'Usa el identificador numérico de la categoría.'})
            productos = productos.filter(categoria_id=int(categoria))
        if params.get('disponibles') == '1':
            productos = productos.filter(cantidad_disponible__gt=0)
        if params.get('ofertas') == '1':
            productos = productos.filter(descuento_porcentaje__gt=0, cantidad_disponible__gt=0)
        ordenes = {'nombre': 'nombre', 'precio_asc': 'precio_calculado', 'precio_desc': '-precio_calculado'}
        orden = params.get('orden', 'nombre')
        if orden not in ordenes:
            raise ValidationError({'orden': 'Orden no reconocido.'})
        if orden != 'nombre':
            from django.db.models import F, DecimalField, ExpressionWrapper
            productos = productos.annotate(precio_calculado=ExpressionWrapper(
                F('precio') * (100 - F('descuento_porcentaje')) / 100.0,
                output_field=DecimalField(max_digits=11, decimal_places=4)))
        return productos.order_by(ordenes[orden], 'id')


class Recomendaciones(APIView):
    def get(self, request):
        base_id = request.query_params.get('producto')
        disponibles = Producto.objects.select_related('categoria').filter(cantidad_disponible__gt=0)
        base = None
        if base_id:
            if not base_id.isascii() or not base_id.isdecimal() or len(base_id) > 18:
                raise ValidationError({'producto': 'Usa el identificador numérico del producto.'})
            base = Producto.objects.select_related('categoria').filter(pk=int(base_id)).first()
            if base is None:
                raise NotFound('El producto no existe.')
            complementos = {
                'Cuadernos': ['Escritura', 'Organización'],
                'Escritura': ['Cuadernos'],
                'Organización': ['Cuadernos', 'Escritura'],
            }
            preferidas = complementos.get(base.categoria.nombre, [])
            disponibles = disponibles.exclude(pk=base.pk).annotate(
                afinidad=Case(
                    When(categoria_id=base.categoria_id, then=Value(2)),
                    When(categoria__nombre__in=preferidas, then=Value(1)),
                    default=Value(0), output_field=IntegerField(),
                )
            ).order_by('-afinidad', '-descuento_porcentaje', '-cantidad_disponible', 'id')
        else:
            disponibles = disponibles.order_by('-descuento_porcentaje', '-cantidad_disponible', 'id')
        resultado = []
        for producto in disponibles[:3]:
            dato = dict(ProductoSerializer(producto).data)
            if base and producto.categoria_id == base.categoria_id:
                dato['motivo'] = f'Otra opción de {producto.categoria.nombre.lower()}'
            elif base:
                dato['motivo'] = f'Para acompañar tu {base.nombre.lower()}'
            else:
                dato['motivo'] = 'En promoción' if producto.descuento_porcentaje else 'Disponible para tus apuntes'
            resultado.append(dato)
        return Response(resultado)
