import Button from './Button'
import './ErrorMessage.css'

/**
 * Mensaje de error con botón para volver a intentar.
 * `onRetry` es opcional: sin él, solo se muestra el mensaje.
 */
export default function ErrorMessage({ message, onRetry }) {
  return (
    <div className="error-message" role="alert">
      <p>{message}</p>
      {onRetry && (
        <Button variant="secondary" onClick={onRetry}>
          Reintentar
        </Button>
      )}
    </div>
  )
}
