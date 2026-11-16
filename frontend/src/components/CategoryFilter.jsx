import { Button } from './ui/button'
export default function CategoryFilter({ categorias, seleccionada, onSeleccionar }) {
  return <div className="filters" aria-label="Filtrar por categoría">{[{id: null, nombre: 'Todos'}, ...categorias].map(c => <Button key={c.id ?? 'todos'} type="button" aria-pressed={seleccionada === c.id} className={`filter ${seleccionada === c.id ? 'active' : ''}`} onClick={() => onSeleccionar(c.id)}>{c.nombre}</Button>)}</div>
}
