async function consultar(ruta, signal, parametros = {}) {
  const query = new URLSearchParams(Object.entries(parametros).filter(([, v]) => v !== '' && v !== null && v !== false))
  const respuesta = await fetch(`/api/${ruta}/?${query}`, { signal })
  if (!respuesta.ok) throw new Error(`El servidor respondió ${respuesta.status}`)
  return respuesta.json()
}
export const obtenerProductos = (signal, parametros) => consultar('productos', signal, parametros)
export const obtenerCategorias = (signal) => consultar('categorias', signal)
export const obtenerRecomendaciones = (signal, producto) => consultar('recomendaciones', signal, { producto })
