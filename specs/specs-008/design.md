# Diseño — specs-008

> **Cómo** se construyen los requisitos de `specs/specs-008/requirements.md`.

**Estado:** Aprobado (v1, 2026-10-13)

---

## 1. Bloques

| Bloque | Requisitos | Qué toca |
|---|---|---|
| **1. Formulario** | RF-61 a RF-63 | `quotes` (modelo, reglas, serializer, vista, panel), `site_content` (campos del formulario y panel), `frontend/src/components/quote/` y `utils/` |
| **2. Secciones del inicio** | RF-58 a RF-60 | `site_content` (`ProcessSection`, textos), `Process.jsx`, `Services.jsx`, `ServiceCard.jsx`, `HomePage.jsx` |

---

## 2. Bloque 1 — Formulario

### 2.1 Modelo (`quotes/models.py`)

`Quote` gana dos campos:

```python
remodel_type = models.CharField("tipo de remodelación", max_length=120, blank=True)
square_meters = models.DecimalField("metros cuadrados", max_digits=8, decimal_places=2, null=True, blank=True)
```

- `blank=True` en el modelo porque las cotizaciones anteriores no tienen tipo escrito; la obligación va en el serializer.
- **No se borra nada:** `category`, `category_name`, `estimated_price`, `QuoteItem` y `RemodelArea` se conservan para el historial. Una cotización nueva los deja vacíos.
- Migración `quotes.0009_remodel_type_and_meters`.

### 2.2 API

- `POST /api/quotes/` recibe:
  ```json
  { "name": "...", "email": "...", "phone": "...", "remodel_type": "cocina y baño",
    "location": "Chacao", "square_meters": "45.5", "needs_visit": false,
    "has_photos": true, "message": "...", "privacy_accepted": true, "website": "" }
  ```
  y responde `{ "id": 15, "whatsapp_url": "https://wa.me/..." }`. Ya no envía `estimated_price`.
- Validación: `remodel_type` y `location` obligatorios ("Escribe qué quieres remodelar." / "Escribe la ubicación del espacio."); `square_meters` opcional y mayor que 0; con `needs_visit` se guarda vacío.
- Se elimina `GET /api/quote-categories/`: el formulario ya no pide áreas.
- Honeypot, límite de envíos y privacidad no cambian.

### 2.3 Mensaje de WhatsApp (`quotes/services.py`)

`build_whatsapp_message(quote)`:

```
Hola RP Design, quiero una cotización:

- Nombre: Ana Pérez
- Correo: ana@mail.com
- Teléfono: +584121234567
- Tipo de remodelación: cocina y baño
- Ubicación: Chacao, Caracas
- Metros cuadrados: 45,5 m²                       (solo si los dio)
- No sé los m²: quiero agendar una visita         (solo si lo marcó)
- Tengo fotos del espacio                         (solo si lo marcó)

- Mensaje: …                                      (solo si lo escribió)
```

Se eliminan las funciones que ya nadie usa: `calculate_estimate`, `calculate_total`, `describe_item` y `area_belongs_to_category`. Se conservan `format_usd` (el panel muestra el estimado de las cotizaciones anteriores), `format_square_meters`, `clean_phone` y `build_whatsapp_link`.

### 2.4 Campos del formulario (`site_content`)

Migraciones `site_content.0016` (opciones del campo `key`) y `0017` (datos):
- La fila `category` pasa a `remodel_type`; su texto de ejemplo cambia a "cocina, patio, baño, casa, quinta, etc." si seguía con el original.
- Se borran las filas `areas` y `area_other`.
- Orden: nombre, teléfono, correo, tipo, ubicación, m², visita, fotos, mensaje.

### 2.5 Panel

- `QuoteAdmin`: muestra `remodel_type`, `location`, `square_meters`, `needs_visit` y `has_photos`. En la lista, la columna "Tipo" usa el tipo escrito o, en las cotizaciones anteriores, el nombre de la categoría. La tabla de áreas y el estimado solo se ven en las cotizaciones que los tienen.
- Se retira del panel `RemodelAreaAdmin` ("Áreas y precios"), el bloque "Calculadora" de "Configuración general" y la columna "Áreas del formulario" de las categorías. Los modelos y sus datos quedan.

### 2.6 Frontend

- `QuoteCalculator.jsx`: campos nombre, teléfono, correo, tipo (texto), ubicación, m² (texto con teclado numérico), casilla de visita, casilla de fotos, mensaje y privacidad. Ya no pide datos a la API antes de mostrarse.
- Se borran `AreaItem.jsx`, `SquareMetersSlider.jsx`, `EstimateDisplay.jsx`, `utils/currency.js` y sus tests; de `utils/estimate.js` queda solo `parseDecimal` (pasa a `utils/numbers.js`).
- `quoteValidation.js`: tipo y ubicación obligatorios; m² opcional, y si se escribe debe ser un número mayor que 0.

---

## 3. Bloque 2 — Secciones del inicio

### 3.1 Modelo (`site_content`)

- `ProcessSection`: `show_video` (casilla, por defecto marcada). El campo `intro` ya existía. En el panel la sección pasa a llamarse "Proceso" (antes "Proceso (encabezado)"). Migraciones `site_content.0019` (esquema) y `0020` (títulos).
- Migración de datos: si `ServicesSection.title` sigue siendo "Un solo equipo para todo tu proyecto", ese título y su introducción pasan a `ProcessSection`, y `ServicesSection` queda con "Servicios" y sin introducción. Si el cliente ya los cambió, no se toca nada.
- `/api/site/`: `process` agrega `intro` y `show_video`.

### 3.2 Frontend

- `Process.jsx`: sección clara con encabezado (título e introducción) y cuadrícula de tarjetas numeradas, con el estilo que tenían las tarjetas de servicio antes de specs-004 (contorno fino, número grande, título y descripción). El video va debajo del encabezado si `show_video` y hay video.
- `ServiceCard.jsx`: se quita el número.
- `HomePage.jsx`: el orden pasa a Hero → Servicios → Proyectos → Proceso → Contacto. Servicios y Proyectos son dos secciones negras seguidas; se distinguen por sus títulos y por el espacio entre ellas.

---

## 4. Registro de decisiones

| Decisión | Motivo |
|---|---|
| Conservar `QuoteItem`, `RemodelArea` y los campos de precio | El historial de cotizaciones debe seguir viéndose; y si el cliente vuelve a pedir precios, los datos siguen ahí |
| Retirar del panel lo que ya no tiene efecto | Un interruptor que no hace nada confunde al cliente |
| Renombrar la fila `category` a `remodel_type` | El nombre del campo coincide con lo que es ahora |
| Mover el título a Proceso con una migración condicionada | Respeta lo que el cliente haya escrito |
