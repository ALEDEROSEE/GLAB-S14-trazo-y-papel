import { Card, CardContent } from './ui/card'

export default function ProductCard({ producto, onRecomendar, compacto = false }) {
  const { nombre, descripcion, precio, precio_final, imagen, categoria_nombre, cantidad_disponible: cantidad, descuento_porcentaje, motivo } = producto
  return <Card className={`product-card ${compacto ? 'compact' : ''}`} data-producto={producto.id}>
    <div className="product-image">
      <img src={imagen} alt={nombre} loading="lazy" />
      <span className="product-category">{categoria_nombre}</span>
      {descuento_porcentaje > 0 && <span className="discount-badge">−{descuento_porcentaje}%</span>}
    </div>
    <CardContent className="product-info">
      <h3>{nombre}</h3>
      <div className="product-price"><strong>S/ {Number(precio_final ?? precio).toFixed(2)}</strong>{descuento_porcentaje > 0 && <del aria-label="Precio anterior">S/ {Number(precio).toFixed(2)}</del>}</div>
      <p>{compacto ? motivo : descripcion}</p>
      <div className="product-bottom"><span className={cantidad ? 'stock' : 'stock empty'}>{cantidad ? cantidad <= 3 ? `Últimas ${cantidad} unidades` : `${cantidad} disponibles` : 'Agotado'}</span>
        {!compacto && <button className="suggest-button" type="button" onClick={() => onRecomendar(producto)} aria-label={`Ver sugerencias para ${nombre}`}>Combínalo <span aria-hidden="true">↗</span></button>}
      </div>
    </CardContent>
  </Card>
}
