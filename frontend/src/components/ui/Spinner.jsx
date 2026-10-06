import './Spinner.css'

/** Indicador de carga: una barra que avanza, con un texto que lo explica. */
export default function Spinner({ label = 'Cargando…' }) {
  return (
    <div className="spinner" role="status">
      <span className="spinner__bar" aria-hidden="true" />
      <span>{label}</span>
    </div>
  )
}
