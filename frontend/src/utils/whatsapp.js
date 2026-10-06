// Enlaces de WhatsApp que arma el propio sitio (botón flotante y Contacto).
// El enlace de la cotización no pasa por aquí: lo arma el backend, que es
// quien calcula el precio y redacta el mensaje.

/**
 * Devuelve https://wa.me/<número>?text=<mensaje>.
 * Sin mensaje, devuelve solo el enlace al número.
 *
 * number:  número en formato internacional; se ignora todo lo que no sea dígito
 * message: texto que aparece ya escrito al abrir el chat (opcional)
 */
export function buildWhatsAppLink(number, message = '') {
  const digits = String(number).replace(/\D/g, '')
  const link = `https://wa.me/${digits}`
  if (!message) return link
  return `${link}?text=${encodeURIComponent(message)}`
}
