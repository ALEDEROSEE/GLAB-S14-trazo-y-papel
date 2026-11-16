from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from .models import Categoria, Producto


class CatalogoApiTests(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre='Cuadernos')
        self.producto = Producto.objects.create(nombre='A5', descripcion='Punteado', precio=Decimal('28.90'), imagen='/a.svg', cantidad_disponible=2, categoria=self.categoria)

    def test_listados_incluyen_datos_y_relacion(self):
        categorias = self.client.get(reverse('categorias')).json()
        productos = self.client.get(reverse('productos')).json()
        self.assertEqual(categorias[0]['nombre'], 'Cuadernos')
        self.assertEqual(productos[0]['categoria'], self.categoria.id)
        self.assertEqual(productos[0]['categoria_nombre'], 'Cuadernos')
        self.assertEqual(productos[0]['precio'], '28.90')

    def test_cambio_en_base_se_refleja_en_el_listado(self):
        self.producto.precio = Decimal('19.90')
        self.producto.save()
        self.assertEqual(self.client.get(reverse('productos')).json()[0]['precio'], '19.90')

    def test_endpoints_son_solo_lectura(self):
        self.assertEqual(self.client.post(reverse('productos'), {}).status_code, 405)
