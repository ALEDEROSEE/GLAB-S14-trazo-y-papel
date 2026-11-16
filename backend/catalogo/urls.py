from django.urls import path
from .views import CategoriaList, ProductoList, Recomendaciones

urlpatterns = [
    path('categorias/', CategoriaList.as_view(), name='categorias'),
    path('productos/', ProductoList.as_view(), name='productos'),
    path('recomendaciones/', Recomendaciones.as_view(), name='recomendaciones'),
]
