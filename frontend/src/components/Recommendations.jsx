import { useEffect, useState } from 'react'
import { obtenerRecomendaciones } from '../services/catalogo'
import ProductCard from './ProductCard'

export default function Recommendations({ elegido }) {
  const [productos, setProductos] = useState([])
  const [estado, setEstado] = useState('cargando')
  useEffect(() => {
    const controller = new AbortController()
    setEstado('cargando')
    obtenerRecomendaciones(controller.signal, elegido?.id ?? '')
      .then(datos => { setProductos(datos); setEstado('listo') })
      .catch(error => { if (error.name !== 'AbortError') setEstado('error') })
    return () => controller.abort()
  }, [elegido])
  return <section className="recommendations" id="recomendaciones" aria-labelledby="recommendations-title">
    <div className="section-heading"><div><p className="eyebrow">UNA IDEA LLEVA A OTRA</p><h2 id="recommendations-title">{elegido ? 'Combina tus favoritos' : 'Para tu próxima idea'}<span>.</span></h2>
      <p>{elegido ? `Sugerencias para ${elegido.nombre.toLowerCase()}.` : 'Artículos disponibles que puedes sumar a tus apuntes.'}</p></div></div>
    {estado === 'cargando' ? <p role="status">Buscando sugerencias…</p> : estado === 'error' ? <p role="alert">No pudimos cargar las sugerencias. Vuelve a elegir un producto.</p> : productos.length ? <div className="product-grid" aria-label="Productos recomendados">{productos.map(p => <ProductCard key={p.id} producto={p} compacto />)}</div> : <p>No hay otros productos disponibles por ahora.</p>}
  </section>
}
