import { useSite } from '../context/SiteContext'

/*
  Página de inicio. Por ahora es una página provisional que comprueba que
  los tokens, las fuentes y la API funcionan. Las secciones reales llegan
  en las tareas T-3.5 a T-3.8.
*/
export default function HomePage() {
  const { data: site, loading, error } = useSite()

  if (loading) return <p className="container">Cargando…</p>
  if (error) return <p className="container">{error.message}</p>

  return (
    <main className="container">
      <h1>{site.hero.title}</h1>
      <p>{site.hero.body}</p>
    </main>
  )
}
