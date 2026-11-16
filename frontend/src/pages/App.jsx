import { useEffect, useState } from 'react'
import Header from '../components/Header'
import CategoryFilter from '../components/CategoryFilter'
import ProductList from '../components/ProductList'
import { obtenerCategorias, obtenerProductos } from '../services/catalogo'
import Recommendations from '../components/Recommendations'

export default function App() {
  const [productos, setProductos] = useState([])
  const [categorias, setCategorias] = useState([])
  const [seleccionada, setSeleccionada] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const [intento, setIntento] = useState(0)
  const [buscar, setBuscar] = useState('')
  const [busqueda, setBusqueda] = useState('')
  const [disponibles, setDisponibles] = useState(false)
  const [ofertas, setOfertas] = useState(false)
  const [orden, setOrden] = useState('nombre')
  const [elegido, setElegido] = useState(null)
  useEffect(() => {
    const timer = setTimeout(() => setBusqueda(buscar.trim()), 280)
    return () => clearTimeout(timer)
  }, [buscar])
  useEffect(() => {
    const controller = new AbortController()
    setCargando(true); setError('')
    Promise.all([obtenerProductos(controller.signal, {
      buscar: busqueda, categoria: seleccionada, disponibles: disponibles ? 1 : '',
      ofertas: ofertas ? 1 : '', orden,
    }), obtenerCategorias(controller.signal)])
      .then(([p, c]) => { setProductos(p); setCategorias(c) })
      .catch(err => { if (err.name !== 'AbortError') setError('No pudimos cargar el catálogo. Revisa que el servidor esté activo.') })
      .finally(() => { if (!controller.signal.aborted) setCargando(false) })
    return () => controller.abort()
  }, [intento, busqueda, seleccionada, disponibles, ofertas, orden])
  function limpiar() {
    setBuscar(''); setBusqueda(''); setSeleccionada(null); setDisponibles(false); setOfertas(false); setOrden('nombre')
  }
  function recomendar(producto) {
    setElegido(producto)
    document.querySelector('#recomendaciones')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
  return <>
    <div className="promo-strip">MÁS IDEAS, MENOS GASTO <span>Hasta 20% en artículos seleccionados</span><a href="#catalogo" onClick={() => { limpiar(); setOfertas(true) }}>Ver ofertas ↗</a></div>
    <Header />
    <main id="inicio">
      <section className="hero"><div><p className="eyebrow">PAPELERÍA PARA TODOS LOS DÍAS</p><h1>Buenas ideas<br /><em>empiezan aquí.</em></h1><p className="hero-copy">Cuadernos, colores y pequeños detalles para acompañarte en cada proyecto.</p><a className="hero-link" href="#catalogo">Explorar el catálogo <span>↗</span></a></div><div className="hero-art"><span className="art-sun">✺</span><span className="art-note">un espacio<br />para crear</span><div className="art-book"><span>IDEAS<br />EN PAPEL</span><i>✳</i></div><span className="art-label">EST. 2026 · AREQUIPA</span></div></section>
      <section className="catalog" id="catalogo" aria-labelledby="catalog-title">
        <div className="section-heading"><div><p className="eyebrow">NUESTROS FAVORITOS</p><h2 id="catalog-title">Encuentra tu próximo favorito<span>.</span></h2><p>Objetos sencillos para organizar, escribir y crear.</p></div><span className="count" aria-live="polite">{!cargando && !error ? `${productos.length} ${productos.length === 1 ? 'producto' : 'productos'}` : ''}</span></div>
        <div className="search-row"><label className="search-field"><span>Buscar en la tienda</span><input type="search" placeholder="Cuaderno, tinta gel, planificador…" value={buscar} onChange={e => setBuscar(e.target.value)} /></label><label className="sort-field"><span>Ordenar por</span><select value={orden} onChange={e => setOrden(e.target.value)}><option value="nombre">Nombre</option><option value="precio_asc">Menor precio</option><option value="precio_desc">Mayor precio</option></select></label></div>
        <CategoryFilter categorias={categorias} seleccionada={seleccionada} onSeleccionar={setSeleccionada} />
        <div className="filter-options"><label><input type="checkbox" checked={disponibles} onChange={e => setDisponibles(e.target.checked)} /> Solo disponibles</label><label><input type="checkbox" checked={ofertas} onChange={e => setOfertas(e.target.checked)} /> En oferta</label><button type="button" onClick={limpiar}>Limpiar filtros</button></div>
        {cargando ? <p className="state-message" role="status">Cargando catálogo…</p> : error ? <div className="state-message" role="alert"><p>{error}</p><button onClick={() => setIntento(n => n + 1)}>Volver a intentar</button></div> : <ProductList productos={productos} onRecomendar={recomendar} />}
      </section>
      <Recommendations elegido={elegido} />
    </main>
    <footer id="nosotros"><div><strong>trazo & papel ✳</strong><p>Papelería para acompañar tus ideas, una página a la vez.</p></div><span>Catálogo de demostración · 2026</span></footer>
  </>
}
