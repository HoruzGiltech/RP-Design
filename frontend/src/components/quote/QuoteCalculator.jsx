import { useState } from 'react'
import { Link } from 'react-router-dom'

import { createQuote, getQuoteCategories } from '../../api/endpoints'
import { useSite } from '../../context/SiteContext'
import { useFetch } from '../../hooks/useFetch'
import { parseDecimal } from '../../utils/estimate'
import { getItemFieldName, MAX_MESSAGE_LENGTH, validateQuote } from '../../utils/quoteValidation'
import Button from '../ui/Button'
import ErrorMessage from '../ui/ErrorMessage'
import Spinner from '../ui/Spinner'
import AreaItem from './AreaItem'
import CheckboxField from './CheckboxField'
import EstimateDisplay from './EstimateDisplay'
import Field from './Field'
import QuoteSuccess from './QuoteSuccess'
import './QuoteCalculator.css'

// Lo que tiene un área recién marcada: 10 m² en la barra y sin texto de "Otro"
const NEW_ITEM = { square_meters: '10', area_other: '' }

const EMPTY_FORM = {
  name: '',
  phone: '',
  email: '',
  category: '',
  location: '',
  // Una entrada por cada área marcada: { [id del área]: { square_meters, area_other } }
  items: {},
  needs_visit: false,
  has_photos: false,
  message: '',
  privacy_accepted: false,
  // Campo trampa para bots (honeypot). Una persona nunca lo ve ni lo llena.
  website: '',
}

// Los campos que el cliente puede retitular desde el panel (specs-003, RF-31)
const TEXT_KEYS = [
  'name',
  'phone',
  'email',
  'category',
  'location',
  'areas',
  'area_other',
  'square_meters',
  'needs_visit',
  'has_photos',
  'message',
]

const BAD_REQUEST = 400
const TOO_MANY_REQUESTS = 429

/**
 * Título y texto de ejemplo de cada campo, tal como están en el panel.
 * Si faltara alguno, queda vacío en lugar de romper el formulario.
 */
function getFieldTexts(formFields = {}) {
  const texts = {}
  for (const key of TEXT_KEYS) {
    texts[key] = { label: '', placeholder: '', ...formFields[key] }
  }
  return texts
}

/**
 * Orden de los campos en pantalla, para llevar el foco al primero con error.
 * Los campos de cada área van en el orden en que aparecen las áreas.
 */
function getFieldOrder(areas) {
  const itemFields = areas.flatMap((area) => [
    getItemFieldName(area.id, 'area_other'),
    getItemFieldName(area.id, 'square_meters'),
  ])
  return [
    'name',
    'phone',
    'email',
    'category',
    'location',
    'items',
    ...itemFields,
    'message',
    'privacy_accepted',
  ]
}

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

  const texts = getFieldTexts(contact.form_fields)
  const selectedCategory = categories.find((category) => String(category.id) === values.category)
  // Solo se ofrecen las áreas del tipo elegido; sin tipo, ninguna
  const areas = selectedCategory ? selectedCategory.areas : []
  // Las áreas marcadas, cada una con lo que la persona llenó
  const selectedItems = areas
    .filter((area) => values.items[area.id])
    .map((area) => ({ area, item: values.items[area.id] }))

  function clearError(name) {
    // Al corregir un campo, su mensaje de error desaparece
    if (errors[name]) {
      setErrors((current) => ({ ...current, [name]: undefined }))
    }
  }

  function handleChange(event) {
    const { name, type, checked, value } = event.target
    // Una casilla no tiene texto: su valor es si está marcada o no
    const newValue = type === 'checkbox' ? checked : value
    setValues((current) => {
      const updated = { ...current, [name]: newValue }
      // Al cambiar el tipo, las áreas marcadas ya no valen: hay que elegirlas de nuevo
      if (name === 'category') updated.items = {}
      return updated
    })
    clearError(name)
  }

  function toggleArea(areaId) {
    setValues((current) => {
      const items = { ...current.items }
      if (items[areaId]) {
        delete items[areaId]
      } else {
        items[areaId] = NEW_ITEM
      }
      return { ...current, items }
    })
    clearError('items')
  }

  function changeItem(areaId, field, value) {
    setValues((current) => ({
      ...current,
      items: { ...current.items, [areaId]: { ...current.items[areaId], [field]: value } },
    }))
    clearError(getItemFieldName(areaId, field))
  }

  function showErrors(newErrors) {
    setErrors(newErrors)
    const firstInvalid = getFieldOrder(areas).find((name) => newErrors[name])
    // El foco va al primer campo con error, para corregirlo sin buscarlo
    if (firstInvalid) document.getElementById(`quote-${firstInvalid}`)?.focus()
  }

  function resetForm() {
    setValues(EMPTY_FORM)
    setErrors({})
    setFormError(null)
    setResult(null)
  }

  /** Lo que se envía al backend: los datos de la persona y un renglón por área marcada. */
  function buildPayload() {
    return {
      ...values,
      category: Number(values.category),
      items: selectedItems.map(({ area, item }) => ({
        area: area.id,
        area_other: area.is_other ? item.area_other : '',
        // Con visita pedida no se envían metros. Si los hay, el backend
        // espera el decimal con punto: "12,5" -> "12.5"
        square_meters: values.needs_visit ? null : String(parseDecimal(item.square_meters)),
      })),
    }
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setFormError(null)

    const validationErrors = validateQuote(values, selectedCategory, settings.max_square_meters)
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
      // El backend responde { campo: ["mensaje"] }: se muestra el primero de cada campo.
      // Los errores de las áreas llegan todos en "items".
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
        as="select"
        name="category"
        label={texts.category.label}
        value={values.category}
        onChange={handleChange}
        error={errors.category}
      >
        {/* En un desplegable, el "texto de ejemplo" es la primera opción, que no elige nada */}
        <option value="">{texts.category.placeholder}</option>
        {categories.map((category) => (
          <option key={category.id} value={category.id}>
            {category.name}
          </option>
        ))}
      </Field>
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

      {/* fieldset + legend: agrupa las casillas bajo una misma pregunta */}
      <fieldset
        className="quote-areas"
        id="quote-items"
        // Recibe el foco si el error es "elige al menos un área"
        tabIndex={-1}
        aria-describedby={errors.items ? 'quote-items-error' : undefined}
      >
        <legend className="quote-field__label">{texts.areas.label}</legend>

        {selectedCategory ? (
          <ul className="quote-areas__list">
            {areas.map((area) => (
              <AreaItem
                key={area.id}
                area={area}
                item={values.items[area.id]}
                needsVisit={values.needs_visit}
                texts={texts}
                max={settings.max_square_meters}
                errors={errors}
                onToggle={() => toggleArea(area.id)}
                onChange={(field, value) => changeItem(area.id, field, value)}
              />
            ))}
          </ul>
        ) : (
          // Las áreas dependen del tipo: hasta elegirlo, no hay nada que ofrecer
          <p className="quote-areas__empty">Elige primero el tipo de remodelación.</p>
        )}

        {errors.items && (
          <span className="quote-field__error" id="quote-items-error">
            {errors.items}
          </span>
        )}
      </fieldset>

      <CheckboxField
        id="quote-needs_visit"
        name="needs_visit"
        className="quote-form__full"
        checked={values.needs_visit}
        onChange={handleChange}
      >
        {texts.needs_visit.label}
      </CheckboxField>

      {/* El cliente puede apagar el estimado desde el panel (specs-003, RF-30) */}
      {settings.show_estimate && (
        <EstimateDisplay
          selectedItems={selectedItems}
          needsVisit={values.needs_visit}
          note={settings.price_note}
        />
      )}

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
