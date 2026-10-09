import { useEffect } from 'react'

// Nombres con los que se registran las fuentes que el cliente carga en el panel
const HEADING_FAMILY = 'RP Titulos'
const BODY_FAMILY = 'RP Texto'

// Las fuentes originales del sitio (las de tokens.css) quedan de respaldo:
// se usan si a la fuente del cliente le falta algún carácter
const HEADING_FALLBACK = "'Archivo Narrow', sans-serif"
const BODY_FALLBACK = "'Archivo', system-ui, sans-serif"

const SAMPLE_TEXT = 'Diseño de interiores'

/**
 * Dice si la fuente cambia de verdad con el grosor (es una fuente "variable").
 * Se mide el mismo texto en normal y en negrita: si mide igual, el archivo
 * trae un solo grosor.
 */
function changesWithWeight(family) {
  const context = document.createElement('canvas').getContext('2d')
  const widthAt = (weight) => {
    context.font = `${weight} 40px "${family}"`
    return context.measureText(SAMPLE_TEXT).width
  }
  return widthAt(400) !== widthAt(800)
}

/** Descarga la fuente y la registra en el navegador con el nombre dado. */
async function registerFont(family, url) {
  const source = `url("${url}")`

  // Primero se registra como fuente variable: un archivo con todos los grosores
  let font = new FontFace(family, source, { weight: '100 900' })
  await font.load()
  document.fonts.add(font)

  // Si el archivo trae un solo grosor, se registra de nuevo sin ese rango.
  // Así el navegador puede engrosarla él mismo para las negritas.
  if (!changesWithWeight(family)) {
    document.fonts.delete(font)
    font = new FontFace(family, source)
    await font.load()
    document.fonts.add(font)
  }
  return font
}

/**
 * Usa una fuente cargada en el panel en lugar de la original del sitio.
 *
 * url:      dirección del archivo, o null si el cliente no cargó ninguna
 * family:   nombre con el que se registra
 * variable: variable de tokens.css que se sobrescribe (--font-display o --font-body)
 * fallback: fuentes de respaldo, las originales del sitio
 */
function useCustomFont(url, family, variable, fallback) {
  useEffect(() => {
    // Sin fuente cargada (o en un navegador muy antiguo) queda la original
    if (!url || !('FontFace' in window)) return undefined

    const root = document.documentElement
    let isCancelled = false
    let registeredFont = null

    registerFont(family, url)
      .then((font) => {
        if (isCancelled) {
          document.fonts.delete(font)
          return
        }
        registeredFont = font
        // La variable se cambia solo cuando la fuente ya está lista: mientras
        // tanto el texto se ve con la fuente original, nunca invisible.
        root.style.setProperty(variable, `'${family}', ${fallback}`)
      })
      // Si el archivo no carga, el sitio sigue con su fuente original
      .catch(() => {})

    return () => {
      isCancelled = true
      if (registeredFont) document.fonts.delete(registeredFont)
      root.style.removeProperty(variable)
    }
  }, [url, family, variable, fallback])
}

/**
 * Aplica las fuentes que el cliente cargó en "Configuración general"
 * (specs-003, RF-19): una para los títulos y otra para el texto.
 */
export function useCustomFonts(settings) {
  useCustomFont(settings?.heading_font, HEADING_FAMILY, '--font-display', HEADING_FALLBACK)
  useCustomFont(settings?.body_font, BODY_FAMILY, '--font-body', BODY_FALLBACK)
}
