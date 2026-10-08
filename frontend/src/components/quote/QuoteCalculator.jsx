import { useState } from 'react'
import { Link } from 'react-router-dom'

import { createQuote, getQuoteCategories } from '../../api/endpoints'
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
import SquareMetersSlider from './SquareMetersSlider'
import './QuoteCalculator.css'

// Metros cuadrados con los que arranca el control deslizante
const INITIAL_SQUARE_METERS = '10'

const EMPTY_FORM = {
  name: '',
  phone: '',
  email: '',
  category: '',
  area: '',
  area_other: '',
  square_meters: INITIAL_SQUARE_METERS,
  message: '',
  privacy_accepted: false,
  // Campo trampa para bots (honeypot). Una persona nunca lo ve ni lo llena.
  website: '',
}

// Orden de los campos en pantalla: sirve para llevar el foco al primero con error
const FIELD_ORDER = [
  'name',
  'phone',
  'email',
  'category',
  'area',
  'area_other',
  'square_meters',
  'message',
  'privacy_accepted',
]

const BAD_REQUEST = 400
const TOO_MANY_REQUESTS = 429

/** Calculadora de cotización: formulario, estimado en vivo y envío por WhatsApp. */
export default function QuoteCalculator() {
  const { data: site } = useSite()
  // Los tipos de remodelación, cada uno con sus áreas (specs-002, RF-17)
  const {
    data: categories,
    loading,
    error: categoriesError,
    reload,
  } = useFetch(getQuoteCategories)

  const [values, setValues] = useState(EMPTY_FORM)
  const [errors, setErrors] = useState({})
  // Error que no es de un campo concreto: sin conexión, demasiados envíos...
  const [formError, setFormError] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  // Respuesta del backend cuando la cotización se guardó
  const [result, setResult] = useState(null)

  const { settings, contact } = site

  if (loading) return <Spinner label="Cargando formulario…" />
  if (categoriesError) return <ErrorMessage message={categoriesError.message} onRetry={reload} />
  if (result) return <QuoteSuccess result={result} onReset={resetForm} />

  const selectedCategory = categories.find((category) => String(category.id) === values.category)
  // Solo se ofrecen las áreas del tipo elegido; sin tipo, ninguna
  const areas = selectedCategory ? selectedCategory.areas : []
  const selectedArea = areas.find((area) => String(area.id) === values.area)
  const squareMeters = parseDecimal(values.square_meters)

  function handleChange(event) {
    const { name, type, checked, value } = event.target
    // Una casilla no tiene texto: su valor es si está marcada o no
    const newValue = type === 'checkbox' ? checked : value
    setValues((current) => {
      const updated = { ...current, [name]: newValue }
      // Al cambiar el tipo, el área elegida ya no vale: hay que elegirla de nuevo
      if (name === 'category') {
        updated.area = ''
        updated.area_other = ''
      }
      return updated
    })
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

    const validationErrors = validateQuote(
      values,
      selectedCategory,
      selectedArea,
      settings.max_square_meters,
    )
    if (Object.keys(validationErrors).length > 0) {
      showErrors(validationErrors)
      return
    }

    setIsSubmitting(true)
    try {
      const response = await createQuote({
        ...values,
        category: Number(values.category),
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
        name="category"
        label="Tipo de remodelación"
        value={values.category}
        onChange={handleChange}
        error={errors.category}
      >
        <option value="">Elige una opción</option>
        {categories.map((category) => (
          <option key={category.id} value={category.id}>
            {category.name}
          </option>
        ))}
      </Field>
      <Field
        as="select"
        name="area"
        label="Área a remodelar"
        value={values.area}
        onChange={handleChange}
        error={errors.area}
        // Las áreas dependen del tipo: hasta elegirlo, no hay nada que ofrecer
        disabled={!selectedCategory}
      >
        <option value="">{selectedCategory ? 'Elige una opción' : 'Elige primero el tipo'}</option>
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
          className="quote-form__area-other"
          placeholder="Ejemplo: terraza"
          value={values.area_other}
          onChange={handleChange}
          error={errors.area_other}
        />
      )}
      <SquareMetersSlider
        value={values.square_meters}
        max={settings.max_square_meters}
        onChange={handleChange}
        error={errors.square_meters}
      />

      <EstimateDisplay area={selectedArea} squareMeters={squareMeters} note={settings.price_note} />

      <Field
        as="textarea"
        name="message"
        className="quote-form__full"
        label="Mensaje (opcional)"
        rows={4}
        placeholder="Cuéntanos qué quieres transformar"
        maxLength={MAX_MESSAGE_LENGTH}
        value={values.message}
        onChange={handleChange}
        error={errors.message}
      />

      <div className="quote-consent">
        <input
          className="quote-consent__checkbox"
          id="quote-privacy_accepted"
          name="privacy_accepted"
          type="checkbox"
          checked={values.privacy_accepted}
          onChange={handleChange}
          aria-invalid={errors.privacy_accepted ? 'true' : undefined}
          aria-describedby={errors.privacy_accepted ? 'quote-privacy_accepted-error' : undefined}
        />
        <label className="quote-consent__label" htmlFor="quote-privacy_accepted">
          Acepto la{' '}
          {/* Se abre en otra pestaña para no perder lo que ya se escribió en el formulario */}
          <Link to="/privacidad" target="_blank" rel="noopener noreferrer">
            política de privacidad
          </Link>{' '}
          y el tratamiento de mis datos para recibir la cotización.
        </label>
        {errors.privacy_accepted && (
          <span className="quote-field__error quote-consent__error" id="quote-privacy_accepted-error">
            {errors.privacy_accepted}
          </span>
        )}
      </div>

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
