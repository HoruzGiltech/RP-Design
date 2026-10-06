import { useState } from 'react'

import { createQuote, getQuoteAreas } from '../../api/endpoints'
import { useSite } from '../../context/SiteContext'
import { useFetch } from '../../hooks/useFetch'
import { parseDecimal } from '../../utils/estimate'
import { MAX_MESSAGE_LENGTH, validateQuote } from '../../utils/quoteValidation'
import Button from '../ui/Button'
import ErrorMessage from '../ui/ErrorMessage'
import Spinner from '../ui/Spinner'
import EstimateDisplay from './EstimateDisplay'
import Field from './Field'
import QuoteSuccess from './QuoteSuccess'
import './QuoteCalculator.css'

const EMPTY_FORM = {
  name: '',
  phone: '',
  email: '',
  area: '',
  area_other: '',
  square_meters: '',
  message: '',
  // Campo trampa para bots (honeypot). Una persona nunca lo ve ni lo llena.
  website: '',
}

// Orden de los campos en pantalla: sirve para llevar el foco al primero con error
const FIELD_ORDER = ['name', 'phone', 'email', 'area', 'area_other', 'square_meters', 'message']

const BAD_REQUEST = 400
const TOO_MANY_REQUESTS = 429

/** Calculadora de cotización: formulario, estimado en vivo y envío por WhatsApp. */
export default function QuoteCalculator() {
  const { data: site } = useSite()
  const { data: areas, loading, error: areasError, reload } = useFetch(getQuoteAreas)

  const [values, setValues] = useState(EMPTY_FORM)
  const [errors, setErrors] = useState({})
  // Error que no es de un campo concreto: sin conexión, demasiados envíos...
  const [formError, setFormError] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  // Respuesta del backend cuando la cotización se guardó
  const [result, setResult] = useState(null)

  const { settings, contact } = site

  if (loading) return <Spinner label="Cargando formulario…" />
  if (areasError) return <ErrorMessage message={areasError.message} onRetry={reload} />
  if (result) return <QuoteSuccess result={result} onReset={resetForm} />

  const selectedArea = areas.find((area) => String(area.id) === values.area)
  const squareMeters = parseDecimal(values.square_meters)

  function handleChange(event) {
    const { name, value } = event.target
    setValues((current) => ({ ...current, [name]: value }))
    // Al corregir un campo, su mensaje de error desaparece
    if (errors[name]) {
      setErrors((current) => ({ ...current, [name]: undefined }))
    }
  }

  function showErrors(newErrors) {
    setErrors(newErrors)
    const firstInvalid = FIELD_ORDER.find((name) => newErrors[name])
    // El foco va al primer campo con error, para corregirlo sin buscarlo
    if (firstInvalid) document.getElementById(`quote-${firstInvalid}`)?.focus()
  }

  function resetForm() {
    setValues(EMPTY_FORM)
    setErrors({})
    setFormError(null)
    setResult(null)
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setFormError(null)

    const validationErrors = validateQuote(values, selectedArea, settings.max_square_meters)
    if (Object.keys(validationErrors).length > 0) {
      showErrors(validationErrors)
      return
    }

    setIsSubmitting(true)
    try {
      const response = await createQuote({
        ...values,
        area: Number(values.area),
        // El backend espera el decimal con punto: "12,5" -> "12.5"
        square_meters: String(squareMeters),
      })
      setResult(response)
      // Misma pestaña (y no una ventana nueva): los navegadores bloquean las
      // ventanas que se abren después de esperar una respuesta del servidor.
      window.location.assign(response.whatsapp_url)
    } catch (submitError) {
      handleSubmitError(submitError)
    } finally {
      setIsSubmitting(false)
    }
  }

  function handleSubmitError(submitError) {
    if (submitError.status === BAD_REQUEST && submitError.data) {
      // El backend responde { campo: ["mensaje"] }: se muestra el primero de cada campo
      const serverErrors = {}
      for (const [field, messages] of Object.entries(submitError.data)) {
        serverErrors[field] = Array.isArray(messages) ? messages[0] : String(messages)
      }
      showErrors(serverErrors)
      return
    }
    if (submitError.status === TOO_MANY_REQUESTS) {
      setFormError('too-many')
      return
    }
    setFormError(submitError.message)
  }

  return (
    <form className="quote-form" onSubmit={handleSubmit} noValidate>
      <Field
        name="name"
        label="Nombre"
        placeholder="Tu nombre"
        autoComplete="name"
        value={values.name}
        onChange={handleChange}
        error={errors.name}
      />
      <Field
        name="phone"
        label="Teléfono"
        type="tel"
        placeholder="0412 000 0000"
        autoComplete="tel"
        value={values.phone}
        onChange={handleChange}
        error={errors.phone}
      />
      <Field
        name="email"
        label="Correo"
        type="email"
        placeholder="nombre@correo.com"
        autoComplete="email"
        value={values.email}
        onChange={handleChange}
        error={errors.email}
      />
      <Field
        as="select"
        name="area"
        label="Área a remodelar"
        value={values.area}
        onChange={handleChange}
        error={errors.area}
      >
        <option value="">Elige una opción</option>
        {areas.map((area) => (
          <option key={area.id} value={area.id}>
            {area.name}
          </option>
        ))}
      </Field>
      {selectedArea?.is_other && (
        <Field
          name="area_other"
          label="Especifica el área"
          placeholder="Ejemplo: terraza"
          value={values.area_other}
          onChange={handleChange}
          error={errors.area_other}
        />
      )}
      <Field
        name="square_meters"
        label="Metros cuadrados"
        // Teclado numérico con coma en el celular
        inputMode="decimal"
        placeholder="Ejemplo: 12,5"
        value={values.square_meters}
        onChange={handleChange}
        error={errors.square_meters}
      />

      <EstimateDisplay area={selectedArea} squareMeters={squareMeters} note={settings.price_note} />

      <Field
        as="textarea"
        name="message"
        label="Mensaje (opcional)"
        rows={4}
        placeholder="Cuéntanos qué quieres transformar"
        maxLength={MAX_MESSAGE_LENGTH}
        value={values.message}
        onChange={handleChange}
        error={errors.message}
      />

      {/*
        Campo trampa (honeypot): los bots llenan todos los campos que encuentran.
        Se oculta con CSS y no con type="hidden", que los bots suelen saltarse.
      */}
      <div className="quote-form__trap" aria-hidden="true">
        <label htmlFor="quote-website">No llenes este campo</label>
        <input
          id="quote-website"
          name="website"
          type="text"
          tabIndex={-1}
          autoComplete="off"
          value={values.website}
          onChange={handleChange}
        />
      </div>

      {formError && (
        <p className="quote-form__error" role="alert">
          {formError === 'too-many' ? (
            <>
              Has enviado muchas solicitudes. Intenta más tarde o{' '}
              <a
                href={`https://wa.me/${settings.whatsapp_number}`}
                target="_blank"
                rel="noopener noreferrer"
              >
                escríbenos directo por WhatsApp
              </a>
              .
            </>
          ) : (
            formError
          )}
        </p>
      )}

      <Button type="submit" className="quote-form__submit" disabled={isSubmitting}>
        {isSubmitting ? 'Enviando…' : contact.submit_text}
      </Button>
    </form>
  )
}
