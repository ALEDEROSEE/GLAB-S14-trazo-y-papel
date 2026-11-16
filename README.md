# Trazo y Papel

Continuación del e-commerce del laboratorio S13 para el laboratorio S14 de Desarrollo de Aplicaciones Empresariales. La base conserva React/Vite, los componentes de shadcn/ui, Django REST Framework, SQLite y los dibujos de los seis artículos de papelería.

La tienda permite consultar el catálogo, buscar por nombre o descripción, combinar categorías con disponibilidad y ofertas, ordenar por el precio rebajado y pedir sugerencias a partir de un producto. El administrador registra entradas y salidas de inventario con motivo, usuario y saldo anterior y posterior.

## Objetivo y público

La aplicación está pensada para estudiantes y personas que compran materiales para escribir u organizar tareas. Busca que puedan encontrar un artículo, comparar su precio y comprobar su disponibilidad desde una computadora o un celular. Es un catálogo de demostración: todavía no incluye carrito, pedidos ni pasarela de pago.

## Ejecutar el backend

Se verificó con Python 3.14, Django 6.1.2 y Django REST Framework 3.18.3.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata catalogo
python manage.py createsuperuser
python manage.py runserver
```

Abrir http://127.0.0.1:8000/admin/. El fixture incorpora tres categorías y seis productos; no incluye usuarios ni contraseñas. Cargarlo de nuevo restablece los productos de demostración, por lo que debe usarse al preparar una base nueva.

## Ejecutar el frontend

Se verificó con Node.js 24.22.1 y Vite 8.3.5. En otra terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Abrir la URL de Vite. Por defecto, `/api` se redirige a Django en el puerto 8000. Para otro puerto de backend, definir `API_TARGET` antes de iniciar Vite, por ejemplo `$env:API_TARGET='http://127.0.0.1:8140'`. Las capturas del informe se tomaron en los puertos 5174 y 8140 para poder conservar el S13 sin interferencias.

## Probar las funciones

En la tienda, buscar `GEL` y elegir Escritura devuelve los lapiceros; al cambiar a Organización se muestra el aviso sin resultados. `Limpiar filtros` recupera los seis productos. Marcar En oferta y ordenar por Menor precio devuelve S/ 19.80, S/ 20.40 y S/ 23.12.

El cuaderno A5 conserva su precio original S/ 28.90 y un descuento del 20 %, por lo que la API devuelve S/ 23.12. Los importes se calculan con Decimal y redondeo a dos decimales en el backend.

En el administrador, abrir Productos y pulsar Registrar movimiento. Registrar una salida de 3 unidades del cuaderno A5 reduce el stock de 12 a 9. Una entrada de 5 lo eleva a 14. Una salida de 99 se rechaza y conserva las 14 unidades y los dos movimientos anteriores. Recargar la tienda permite comprobar el nuevo stock. Las operaciones están restringidas a personal con permiso para cambiar productos y protegidas con CSRF. Los registros de movimientos se consultan sin edición ni borrado desde el administrador.

`Combínalo` consulta sugerencias para el artículo seleccionado. La regla prefiere la misma categoría y luego categorías complementarias; los descuentos y el stock resuelven el orden. No devuelve el artículo seleccionado ni productos agotados. Es una recomendación por reglas, sin historial de clientes ni aprendizaje automático.

## API pública de lectura

| Ruta | Ejemplo |
| --- | --- |
| `/api/categorias/` | Categorías disponibles |
| `/api/productos/` | Catálogo completo |
| `/api/productos/?buscar=gel&categoria=2` | Búsqueda y categoría combinadas |
| `/api/productos/?ofertas=1&orden=precio_asc` | Ofertas ordenadas por precio final |
| `/api/productos/?disponibles=1` | Productos con stock mayor que cero |
| `/api/recomendaciones/?producto=1` | Hasta tres sugerencias para el A5 |

Los parámetros incorrectos de categoría, producto y orden devuelven 400; una recomendación para un producto inexistente devuelve 404. La API pública no modifica inventario.

## Validación

```powershell
cd backend
python manage.py check
python manage.py test catalogo -v 2
```

```powershell
cd frontend
npm run build
```

Pasaron 20 pruebas del backend y la compilación de producción. Las pruebas del navegador comprobaron búsqueda combinada, ofertas, recomendaciones, entradas y salidas y ausencia de desbordamiento horizontal a 360, 390 y 768 píxeles. Las salidas reales se incluyen en `validacion/`.

## Organización y alcance

`backend/catalogo/models.py` define productos y movimientos. `services.py` ejecuta el cambio de stock y su registro dentro de una transacción. `views.py` resuelve los filtros y recomendaciones; `admin.py` publica la pantalla de inventario. Las migraciones conservan la estructura inicial del S13 y añaden los campos y la tabla del S14.

`frontend/src/components` conserva los componentes de la tienda y añade Recommendations. `pages/App.jsx` administra los filtros, la espera de 280 ms al escribir y la cancelación de consultas anteriores. `services/catalogo.js` centraliza las solicitudes.

La configuración incluida es de desarrollo local, con DEBUG activo. Una instalación pública necesitaría un servidor de producción y su configuración de secretos y proxy. El laboratorio no procesa ventas ni representa una tienda operativa con clientes reales.

Base del S13: https://github.com/ALEDEROSEE/GLAB-S13-trazo-y-papel

Alumno: Alvarez Sayaverde Alejandro Aaron. Grupo C. Docente: Jean Marco Miranda Llanos. Fecha: 16/11/2026.
