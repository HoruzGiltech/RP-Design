// Cliente base de la API: todas las llamadas al backend pasan por aquí.

// La dirección de la API sale de frontend/.env (ver .env.example)
const API_URL = import.meta.env.VITE_API_URL

const NETWORK_ERROR_MESSAGE = 'No pudimos conectar con el servidor. Revisa tu conexión e inténtalo de nuevo.'
const GENERIC_ERROR_MESSAGE = 'Ocurrió un error inesperado. Inténtalo de nuevo.'

/**
 * Error de una llamada a la API.
 * - status: código HTTP (404, 429...). Vale 0 si no hubo respuesta del servidor.
 * - data: lo que respondió el backend. En un 400 son los errores de cada campo.
 */
export class ApiError extends Error {
  constructor(message, status, data = null) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.data = data
  }
}

async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`${API_URL}${path}`, options)
  } catch {
    // fetch solo falla así cuando no hay red o el servidor no responde
    throw new ApiError(NETWORK_ERROR_MESSAGE, 0)
  }

  // Una respuesta de error puede no traer JSON (por ejemplo, un 500)
  const data = await response.json().catch(() => null)

  if (!response.ok) {
    throw new ApiError(GENERIC_ERROR_MESSAGE, response.status, data)
  }
  return data
}

export function apiGet(path) {
  return request(path)
}

export function apiPost(path, body) {
  return request(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}
