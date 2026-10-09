import { getItemFieldName } from '../../utils/quoteValidation'
import CheckboxField from './CheckboxField'
import Field from './Field'
import SquareMetersSlider from './SquareMetersSlider'

/**
 * Un área del formulario: su casilla y, cuando está marcada, sus propios
 * campos (specs-003, RF-27): los metros cuadrados y, si es "Otro", el texto
 * para especificarla.
 *
 * area:       el área (objeto de la API)
 * item:       lo que la persona llenó para esta área ({ square_meters, area_other }),
 *             o undefined si no está marcada
 * needsVisit: true si marcó "no sé cuántos m² son": entonces no se piden metros
 * texts:      títulos y textos de ejemplo de los campos, editables desde el panel
 * max:        máximo de m² configurado en el panel
 * errors:     errores del formulario (se leen los de esta área)
 * onToggle:   se llama al marcar o desmarcar la casilla
 * onChange:   se llama con (campo, valor) al cambiar uno de sus campos
 */
export default function AreaItem({
  area,
  item,
  needsVisit,
  texts,
  max,
  errors,
  onToggle,
  onChange,
}) {
  const isSelected = Boolean(item)
  const otherName = getItemFieldName(area.id, 'area_other')
  const metersName = getItemFieldName(area.id, 'square_meters')
  // Sin nada más que pedir, la tarjeta se queda solo con la casilla
  const hasDetails = isSelected && (area.is_other || !needsVisit)

  return (
    <li className={isSelected ? 'quote-area is-selected' : 'quote-area'}>
      <CheckboxField
        id={`quote-area-${area.id}`}
        name={`area-${area.id}`}
        checked={isSelected}
        onChange={onToggle}
      >
        {area.name}
      </CheckboxField>

      {hasDetails && (
        <div className="quote-area__details">
          {area.is_other && (
            <Field
              name={otherName}
              label={texts.area_other.label}
              placeholder={texts.area_other.placeholder}
              value={item.area_other}
              onChange={(event) => onChange('area_other', event.target.value)}
              error={errors[otherName]}
            />
          )}
          {!needsVisit && (
            <SquareMetersSlider
              id={`quote-${metersName}`}
              label={texts.square_meters.label}
              areaName={area.name}
              value={item.square_meters}
              max={max}
              onChange={(value) => onChange('square_meters', value)}
              error={errors[metersName]}
            />
          )}
        </div>
      )}
    </li>
  )
}
