import ProductCard from './ProductCard'
export default function ProductList({ productos, onRecomendar }) {
  if (!productos.length) return <p className="state-message" role="status">No encontramos productos con esos filtros. Prueba otra búsqueda o limpia los filtros.</p>
  return <div className="product-grid">{productos.map(p => <ProductCard key={p.id} producto={p} onRecomendar={onRecomendar} />)}</div>
}
