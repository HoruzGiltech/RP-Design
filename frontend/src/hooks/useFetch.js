import { useCallback, useEffect, useState } from 'react'

/**
 * Pide datos a la API y lleva la cuenta de los tres estados de siempre.
 *
 *   const { data, loading, error, reload } = useFetch(getProjects)
 *
 * `fetcher` es una función que devuelve una promesa (las de api/endpoints.js).
 * Si depende de un valor que puede cambiar, como el slug de la URL, se pasa
 * en `deps` para que los datos se vuelvan a pedir cuando cambie:
 *
 *   useFetch(() => getProject(slug), [slug])
 */
export function useFetch(fetcher, deps = []) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  // Cambiar este número fuerza una nueva petición (botón "Reintentar")
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    // Si el componente desaparece o cambian las deps antes de que llegue
    // la respuesta, esa respuesta ya no interesa y se ignora.
    let ignore = false

    setLoading(true)
    setError(null)

    fetcher()
      .then((result) => {
        if (!ignore) setData(result)
      })
      .catch((fetchError) => {
        if (!ignore) setError(fetchError)
      })
      .finally(() => {
        if (!ignore) setLoading(false)
      })

    return () => {
      ignore = true
    }
    // `fetcher` no va en la lista: suele ser una función nueva en cada render
    // y provocaría peticiones sin fin. Quien usa el hook indica las deps reales.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, attempt])

  const reload = useCallback(() => setAttempt((current) => current + 1), [])

  return { data, loading, error, reload }
}
