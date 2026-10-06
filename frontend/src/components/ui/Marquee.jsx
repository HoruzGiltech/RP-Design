import './Marquee.css'

// Cuántas veces se repite la lista dentro de cada mitad de la cinta.
// Con pocos elementos cortos, una sola copia no alcanza a llenar una pantalla ancha.
const REPEAT = 4

/**
 * Cinta de textos que se desplaza sin parar (specs/design.md §3.6).
 *
 * Cómo funciona: la cinta tiene dos mitades idénticas, una a continuación de
 * la otra. La animación la mueve hacia la izquierda exactamente una mitad y
 * vuelve a empezar; como las dos mitades son iguales, el salto no se nota.
 *
 * Accesibilidad:
 * - Las copias son solo decoración (aria-hidden). Un lector de pantalla lee
 *   la lista real, que está aparte, una sola vez.
 * - Se detiene con el cursor encima o al recibir el foco del teclado.
 * - Con "reducir movimiento" la cinta no se muestra: se ve la lista fija.
 *
 * items: lista de { id, text }.  label: nombre de la lista para lectores de pantalla.
 */
export default function Marquee({ items, label }) {
  const half = Array.from({ length: REPEAT }, () => items).flat()

  return (
    <div className="marquee" role="group" aria-label={label} tabIndex={0}>
      <ul className="marquee__list">
        {items.map((item) => (
          <li key={item.id}>{item.text}</li>
        ))}
      </ul>

      <div className="marquee__track" aria-hidden="true">
        {[0, 1].map((halfNumber) => (
          <div className="marquee__half" key={halfNumber}>
            {half.map((item, position) => (
              <span className="marquee__item" key={position}>
                {item.text}
              </span>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}
