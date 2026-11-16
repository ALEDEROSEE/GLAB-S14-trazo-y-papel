from django import forms
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html
from .models import Categoria, Producto, MovimientoInventario
from .services import registrar_movimiento

admin.site.site_header = 'Trazo y Papel · Administración'
admin.site.site_title = 'Trazo y Papel'
admin.site.index_title = 'Catálogo e inventario'


class MovimientoForm(forms.Form):
    tipo = forms.ChoiceField(choices=MovimientoInventario.Tipo.choices)
    cantidad = forms.IntegerField(min_value=1, label='Unidades')
    motivo = forms.CharField(max_length=160, label='Motivo del movimiento')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    search_fields = ['nombre']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'precio', 'descuento_porcentaje',
                    'cantidad_disponible', 'estado_stock', 'gestionar']
    list_filter = ['categoria']
    search_fields = ['nombre']
    readonly_fields = ['cantidad_disponible', 'gestionar']

    @admin.display(description='Estado')
    def estado_stock(self, obj):
        if not obj.cantidad_disponible:
            return 'Agotado'
        return 'Stock bajo' if obj.cantidad_disponible <= 3 else 'Disponible'

    @admin.display(description='Inventario')
    def gestionar(self, obj):
        if not obj.pk:
            return 'Guarda el producto y registra su primera entrada.'
        return format_html('<a href="{}">Registrar movimiento</a>',
                           reverse('admin:catalogo_producto_inventario', args=[obj.pk]))

    def get_urls(self):
        return [path('<int:producto_id>/inventario/', self.admin_site.admin_view(self.inventario),
                     name='catalogo_producto_inventario')] + super().get_urls()

    def inventario(self, request, producto_id):
        producto = get_object_or_404(Producto, pk=producto_id)
        if not self.has_change_permission(request, producto):
            raise PermissionDenied
        form = MovimientoForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            try:
                movimiento = registrar_movimiento(producto=producto, usuario=request.user, **form.cleaned_data)
            except ValidationError as error:
                form.add_error(None, error)
            else:
                messages.success(request, f'{movimiento.get_tipo_display()} registrada: '
                                 f'{movimiento.stock_anterior} → {movimiento.stock_posterior} unidades.')
                return redirect(request.path)
        return TemplateResponse(request, 'admin/catalogo/inventario.html', {
            **self.admin_site.each_context(request), 'title': f'Inventario de {producto.nombre}',
            'producto': producto, 'form': form,
            'movimientos': producto.movimientos.select_related('usuario')[:20],
            'opts': self.model._meta,
        })


@admin.register(MovimientoInventario)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ['creado', 'producto', 'tipo', 'cantidad', 'stock_anterior', 'stock_posterior', 'usuario', 'motivo']
    list_filter = ['tipo', 'producto']
    search_fields = ['motivo', 'producto__nombre']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
