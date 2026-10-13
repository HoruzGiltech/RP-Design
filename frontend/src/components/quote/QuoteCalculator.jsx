import { useState } from 'react'
import { Link } from 'react-router-dom'

import { createQuote } from '../../api/endpoints'
import { useSite } from '../../context/SiteContext'
import { keepNumberCharacters, parseDecimal } from '../../utils/numbers'
import { MAX_MESSAGE_LENGTH, validateQuote } from '../../utils/quoteValidation'
import Button from '../ui/Button'
import CheckboxField from './CheckboxField'
import Field from './Field'
import QuoteSuccess from './QuoteSuccess'
import './QuoteCalculator.css'

const EMPTY_FORM = {
  name: '',
  phone: '',
  email: '',
  // Texto libre: lo que la persona quiere remodelar (specs-008)
  remodel_type: '',
  location: '',
  square_meters: '',
  needs_visit: false,
  has_photos: false,
  message: '',
  privacy_accepted: false,
  // Campo trampa para bots (honeypot). Una persona nunca lo ve ni lo llena.
  website: '',
}

// Orden de los campos en pantalla: sirve para llevar el foco al primero con error.
// Son también los campos que el cliente puede retitular desde el panel (RF-31),
// salvo la casilla de privacidad.
const FIELD_ORDER = [
  'name',
  'phone',
  'email',
  'remodel_type',
  'location',
  'square_meters',
  'needs_visit',
  'has_photos',
  'message',
  'privacy_accepted',
]

const BAD_REQUEST = 400
const TOO_MANY_REQUESTS = 429

/**
 * Título y texto de ejemplo de cada campo, tal como están en el panel.
 * Si faltara alguno, queda vacío en lugar de romper el formulario.
 */
function getFieldTexts(formFields = {}) {
  const texts = {}
  for (const key of FIELD_ORDER) {
    texts[key] = { label: '', placeholder: '', ...formFields[key] }
  }
  return texts
}

/**
 * Formulario de cotización: datos de contacto, qué se quiere remodelar y
 * envío por WhatsApp. Desde specs-008 no calcula ningún precio.
 * (El nombre del componente viene de cuando tenía una calculadora.)
 */
export default function QuoteCalculator() {
  const { data: site } = useSite()

  const [values, setValues] = useState(EMPTY_FORM)
  const [errors, setErrors] = useState({})
  // Error que no es de un campo concreto: sin conexión, demasiados envíos...
  const [formError, setFormError] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  // Respuesta del backend cuando la cotización se guardó
  const [result, setResult] = useState(null)

  const { settings, contact } = site

  if (result) return <QuoteSuccess result={result} onReset={resetForm} />

  const texts = getFieldTexts(contact.form_fields)

  function handleChange(event) {
    const { name, type, checked, value } = event.target
    // Una casilla no tiene texto: su valor es si está marcada o no
    let newValue = type === 'checkbox' ? checked : value
    // Los metros son un campo numérico: lo que no sea cifra, coma o punto no se escribe
    if (name === 'square_meters') newValue = keepNumberCharacters(value)
    setValues((current) => ({ ...current, [name]: newValue }))
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

  /** Lo que se envía al backend. */
  function buildPayload() {
    const wroteSquareMeters = values.square_meters.trim() !== ''
    const sendsSquareMeters = wroteSquareMeters && !values.needs_visit
    return {
      ...values,
      // Sin metros (o con visita pedida) se envía vacío. Si los hay, el backend
      // espera el decimal con punto: "12,5" -> "12.5"
      square_meters: sendsSquareMeters ? String(parseDecimal(values.square_meters)) : null,
    }
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setFormError(null)

    const validationErrors = validateQuote(values)
    if (Object.keys(validationErrors).length > 0) {
      showErrors(validationErrors)
      return
    }

    setIsSubmitting(true)
    try {
      const response = await createQuote(buildPayload())
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
        serverErrors[field] = Array.isArray(messages) ? String(messages[0]) : String(messages)
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
        label={texts.name.label}
        placeholder={texts.name.placeholder}
        autoComplete="name"
        value={values.name}
        onChange={handleChange}
        error={errors.name}
      />
      <Field
        name="phone"
        label={texts.phone.label}
        type="tel"
        placeholder={texts.phone.placeholder}
        autoComplete="tel"
        value={values.phone}
        onChange={handleChange}
        error={errors.phone}
      />
      <Field
        name="email"
        label={texts.email.label}
        type="email"
        placeholder={texts.email.placeholder}
        autoComplete="email"
        value={values.email}
        onChange={handleChange}
        error={errors.email}
      />
      <Field
        name="remodel_type"
        label={texts.remodel_type.label}
        placeholder={texts.remodel_type.placeholder}
        autoComplete="off"
        maxLength={120}
        value={values.remodel_type}
        onChange={handleChange}
        error={errors.remodel_type}
      />
      <Field
        name="location"
        label={texts.location.label}
        placeholder={texts.location.placeholder}
        autoComplete="off"
        maxLength={160}
        value={values.location}
        onChange={handleChange}
        error={errors.location}
      />
      <Field
        name="square_meters"
        label={texts.square_meters.label}
        placeholder={texts.square_meters.placeholder}
        // Campo numérico: solo acepta cifras, coma y punto (ver handleChange).
        // Es type="text" y no "number" para poder escribir la coma decimal (12,5)
        // en cualquier navegador; inputMode abre el teclado numérico en el celular.
        type="text"
        inputMode="decimal"
        autoComplete="off"
        // Quien pide una visita no sabe los metros: el campo no aplica
        disabled={values.needs_visit}
        value={values.needs_visit ? '' : values.square_meters}
        onChange={handleChange}
        error={errors.square_meters}
      />

      <CheckboxField
        id="quote-needs_visit"
        name="needs_visit"
        className="quote-form__full"
        checked={values.needs_visit}
        onChange={handleChange}
      >
        {texts.needs_visit.label}
      </CheckboxField>

      <CheckboxField
        id="quote-has_photos"
        name="has_photos"
        className="quote-form__full"
        checked={values.has_photos}
        onChange={handleChange}
      >
        {texts.has_photos.label}
      </CheckboxField>

      <Field
        as="textarea"
        name="message"
        className="quote-form__full"
        label={texts.message.label}
        rows={4}
        placeholder={texts.message.placeholder}
        maxLength={MAX_MESSAGE_LENGTH}
        value={values.message}
        onChange={handleChange}
        error={errors.message}
      />

      <CheckboxField
        id="quote-privacy_accepted"
        name="privacy_accepted"
        className="quote-form__full quote-check--small"
        checked={values.privacy_accepted}
        onChange={handleChange}
        error={errors.privacy_accepted}
      >
        Acepto la{' '}
        {/* Se abre en otra pestaña para no perder lo que ya se escribió en el formulario */}
        <Link to="/privacidad" target="_blank" rel="noopener noreferrer">
          política de privacidad
        </Link>{' '}
        y el tratamiento de mis datos para recibir la cotización.
      </CheckboxField>

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
