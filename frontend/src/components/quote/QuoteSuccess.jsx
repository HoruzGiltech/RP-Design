import { useEffect, useRef } from 'react'

import Button from '../ui/Button'

/**
 * Pantalla que queda en lugar del formulario cuando la cotización se guardó.
 *
 * El sitio intenta abrir WhatsApp solo, pero el navegador puede impedirlo
 * (o la persona puede volver atrás). Por eso siempre queda este botón.
 */
export default function QuoteSuccess({ result, onReset }) {
  const headingRef = useRef(null)

  // El foco pasa al título para que un lector de pantalla anuncie el resultado
  useEffect(() => {
    headingRef.current.focus()
  }, [])

  return (
    <div className="quote-form quote-success">
      <h3 className="quote-success__title" ref={headingRef} tabIndex={-1}>
        Tu solicitud quedó registrada
      </h3>
      {/* Si el cliente apagó el estimado en el panel, el backend no envía el monto */}
      {result.estimated_price_display && (
        <p>
          Estimado: <strong>{result.estimated_price_display}</strong>
        </p>
      )}
      <p className="quote-success__text">
        Solo falta enviar el mensaje por WhatsApp. Si no se abrió solo, usa este botón.
      </p>
      <Button href={result.whatsapp_url} target="_blank" rel="noopener noreferrer">
        Abrir WhatsApp
      </Button>
      <button type="button" className="quote-success__reset" onClick={onReset}>
        Hacer otra cotización
      </button>
    </div>
  )
}
