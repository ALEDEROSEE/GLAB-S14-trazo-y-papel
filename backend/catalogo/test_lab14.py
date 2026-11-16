from decimal import Decimal
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.test import TestCase, Client
from django.urls import reverse
from .models import Categoria, Producto, MovimientoInventario
from .services import registrar_movimiento


class FuncionesLab14Tests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cuadernos = Categoria.objects.create(nombre='Cuadernos')
        cls.escritura = Categoria.objects.create(nombre='Escritura')
        cls.organizacion = Categoria.objects.create(nombre='Organización')
        cls.a = Producto.objects.create(nombre='Cuaderno A5', descripcion='Hojas punteadas',
            precio=Decimal('28.90'), descuento_porcentaje=20, cantidad_disponible=12, categoria=cls.cuadernos)
        cls.b = Producto.objects.create(nombre='Cuaderno bolsillo', descripcion='Rayado',
            precio=Decimal('16.50'), cantidad_disponible=8, categoria=cls.cuadernos)
        cls.c = Producto.objects.create(nombre='Lapiceros', descripcion='Tinta gel negra',
            precio=Decimal('14.90'), cantidad_disponible=20, categoria=cls.escritura)
        cls.d = Producto.objects.create(nombre='Notas adhesivas', descripcion='Papel',
            precio=Decimal('12.50'), descuento_porcentaje=10, cantidad_disponible=0, categoria=cls.organizacion)
        cls.admin = get_user_model().objects.create_superuser('pruebas', password='Solo-tests-142026')

    def api(self, **params):
        return self.client.get(reverse('productos'), params)

    def mover(self, **kwargs):
        datos = dict(producto=self.a, tipo='salida', cantidad=3, motivo='Venta de demostración', usuario=self.admin)
        datos.update(kwargs)
        return registrar_movimiento(**datos)

    def test_busqueda_en_descripcion_y_sin_distinguir_mayusculas(self):
        datos = self.api(buscar='GEL').json()
        self.assertEqual([p['id'] for p in datos], [self.c.id])

    def test_filtros_categoria_busqueda_y_disponibilidad_se_combinan(self):
        datos = self.api(buscar='cuaderno', categoria=self.cuadernos.id, disponibles=1).json()
        self.assertEqual({p['id'] for p in datos}, {self.a.id, self.b.id})
        self.assertEqual(self.api(buscar='gel', categoria=self.cuadernos.id).json(), [])

    def test_descuento_decimal_y_precio_original(self):
        datos = self.api(buscar='A5').json()[0]
        self.assertEqual(datos['precio'], '28.90')
        self.assertEqual(datos['precio_final'], '23.12')
        self.a.precio = Decimal('0.05')
        self.a.descuento_porcentaje = 10
        self.assertEqual(self.a.precio_final, Decimal('0.05'))

    def test_ofertas_excluyen_agotados_y_sin_descuento(self):
        self.assertEqual([p['id'] for p in self.api(ofertas=1).json()], [self.a.id])

    def test_orden_precio_usa_importe_con_descuento(self):
        self.b.descuento_porcentaje = 40
        self.b.save()
        datos = self.api(orden='precio_asc').json()
        self.assertEqual(datos[0]['id'], self.b.id)
        self.assertEqual(datos[-1]['id'], self.a.id)

    def test_parametros_invalidos_responden_400(self):
        for params in [{'categoria': 'abc'}, {'categoria': '²'}, {'orden': 'desconocido'}]:
            with self.subTest(params=params):
                self.assertEqual(self.api(**params).status_code, 400)

    def test_recomendacion_prioriza_categoria_y_excluye_base_y_agotados(self):
        datos = self.client.get(reverse('recomendaciones'), {'producto': self.a.id}).json()
        self.assertEqual(datos[0]['id'], self.b.id)
        self.assertNotIn(self.a.id, [p['id'] for p in datos])
        self.assertNotIn(self.d.id, [p['id'] for p in datos])
        self.assertIn('cuadernos', datos[0]['motivo'])

    def test_recomendacion_sin_contexto_y_producto_inexistente(self):
        datos = self.client.get(reverse('recomendaciones')).json()
        self.assertEqual(datos[0]['id'], self.a.id)
        self.assertEqual(self.client.get(reverse('recomendaciones'), {'producto': 99999}).status_code, 404)
        self.assertEqual(self.client.get(reverse('recomendaciones'), {'producto': '²'}).status_code, 400)

    def test_salida_guarda_saldo_y_usuario(self):
        m = self.mover()
        self.a.refresh_from_db()
        self.assertEqual((m.stock_anterior, m.stock_posterior, self.a.cantidad_disponible), (12, 9, 9))
        self.assertEqual(m.usuario, self.admin)

    def test_entrada_y_salida_hasta_cero(self):
        self.mover(tipo='entrada', cantidad=5)
        m = self.mover(cantidad=17)
        self.assertEqual((m.stock_anterior, m.stock_posterior), (17, 0))

    def test_salida_excesiva_no_cambia_stock_ni_historial(self):
        with self.assertRaisesMessage(ValidationError, 'Stock insuficiente'):
            self.mover(cantidad=13)
        self.a.refresh_from_db()
        self.assertEqual(self.a.cantidad_disponible, 12)
        self.assertFalse(MovimientoInventario.objects.exists())

    def test_rechaza_cero_negativos_fracciones_y_motivo_vacio(self):
        for cantidad in [0, -1, 1.5, True]:
            with self.subTest(cantidad=cantidad), self.assertRaises(ValidationError):
                self.mover(cantidad=cantidad)
        with self.assertRaises(ValidationError):
            self.mover(motivo='   ')

    def test_fallo_al_guardar_historial_revierte_cambio_de_stock(self):
        with patch('catalogo.services.MovimientoInventario.objects.create', side_effect=RuntimeError('Fallo simulado de escritura')):
            with self.assertRaises(RuntimeError):
                self.mover()
        self.a.refresh_from_db()
        self.assertEqual(self.a.cantidad_disponible, 12)

    def test_usuario_sin_permiso_no_puede_mover_stock(self):
        usuario = get_user_model().objects.create_user('lector')
        with self.assertRaises(ValidationError):
            self.mover(usuario=usuario)
        self.assertEqual(MovimientoInventario.objects.count(), 0)

    def test_inventario_admin_requiere_login_permiso_y_csrf(self):
        url = reverse('admin:catalogo_producto_inventario', args=[self.a.id])
        self.assertEqual(self.client.get(url).status_code, 302)
        lector = get_user_model().objects.create_user('personal', is_staff=True)
        self.client.force_login(lector)
        self.assertEqual(self.client.get(url).status_code, 403)
        lector.user_permissions.add(Permission.objects.get(codename='change_producto'))
        self.assertEqual(self.client.get(url).status_code, 200)
        seguro = Client(enforce_csrf_checks=True)
        seguro.force_login(self.admin)
        self.assertEqual(seguro.post(url, {'tipo': 'salida', 'cantidad': 1, 'motivo': 'sin token'}).status_code, 403)

    def test_admin_muestra_error_sin_perder_historial(self):
        self.client.force_login(self.admin)
        url = reverse('admin:catalogo_producto_inventario', args=[self.a.id])
        respuesta = self.client.post(url, {'tipo': 'salida', 'cantidad': 99, 'motivo': 'Prueba de límite'})
        self.assertContains(respuesta, 'Stock insuficiente')
        self.assertFalse(MovimientoInventario.objects.exists())

    def test_descuento_fuera_de_rango_se_rechaza(self):
        self.a.descuento_porcentaje = 90
        with self.assertRaises(ValidationError):
            self.a.full_clean()
