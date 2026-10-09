# Diseño técnico — specs-003

> **Cómo** se construye lo que pide `specs/specs-003/requirements.md`.
> Solo describe lo que cambia. Lo que no aparece aquí sigue como en `specs/design.md` y en los paquetes anteriores.

**Estado:** Borrador v1 (2026-10-09) — pendiente de aprobación

---

## 1. Qué se toca

```
backend/core/           validador de fuentes; permisos de los modelos nuevos
backend/projects/       categoría visible; descripción en las tarjetas
backend/quotes/         cotización con varios renglones; campos nuevos; mensaje
backend/site_content/   fuentes, interruptor de precio, "Cotizar", pasos y servicios
                        dentro de su sección, textos del formulario
frontend/src/           fuentes, hero con video, tarjetas, inicio, formulario y pie
```

No se agregan dependencias, ni en el backend ni en el frontend.

---

## 2. Backend

### 2.1 Validación de fuentes (`core/validators.py`)

```python
FONT_EXTENSIONS = ["woff2", "woff", "ttf", "otf"]

def validate_font_file(file):
    """Valida una fuente: extensión, tamaño (MAX_FONT_MB) y contenido real."""
```

- Mismos tres controles que imágenes y videos, reutilizando `_check_extension` y `_check_size`.
- **Contenido real:** se leen los primeros 4 bytes del archivo y se comparan con la firma de cada formato:

| Formato | Primeros bytes |
|---|---|
| `woff2` | `wOF2` |
| `woff` | `wOFF` |
| `otf` | `OTTO` |
| `ttf` | `00 01 00 00` o `true` |

- `MAX_FONT_MB` en `settings.py`, leído de `.env` (por defecto 2).
- Las fuentes se guardan en `site/<año>/<uuid>.<ext>` con `build_unique_path`, como el resto de archivos del sitio.

### 2.2 Modelos

**SiteSettings** (`site_content`)

| Campo | Notas |
|---|---|
| `heading_font` | File, opcional. "Fuente de títulos". Validado con `validate_font_file` |
| `body_font` | File, opcional. "Fuente de texto" |
| `show_estimate` | Bool, "Mostrar el estimado de precio", por defecto `True` |

**ProjectCategory** (`projects`)

| Campo | Notas |
|---|---|
| `is_visible` | Bool, "mostrar en el sitio", por defecto `True` |

**ServicesSection** (`site_content`)

| Campo | Notas |
|---|---|
| `cta_text` | Char(40), "texto del botón de cada servicio". Por defecto "Cotizar" |

**Service y ProcessStep** (`site_content`)

| Campo | Notas |
|---|---|
| `section` | FK nuevo → su sección (`ServicesSection` / `ProcessSection`), `on_delete=CASCADE`, `related_name="items"` / `"steps"`, `default=1` |

- Las secciones son registros únicos con `pk=1`, así que la relación siempre apunta al mismo registro. Su único propósito es poder editar la lista **dentro** del formulario de la sección (un "inline" de Django necesita esa relación).

**QuoteFormField** (`site_content`) — nuevo

| Campo | Notas |
|---|---|
| `section` | FK → `ContactSection`, `default=1`, `related_name="form_fields"` |
| `key` | Char, único, no editable. Identifica el campo: `name`, `phone`, `email`, `category`, `areas`, `area_other`, `square_meters`, `location`, `message`, `has_photos`, `needs_visit` |
| `label` | Char(120). Título del campo |
| `placeholder` | Char(120), opcional. Texto de ejemplo (las casillas no lo usan) |
| `order` | Para listarlos en el orden del formulario |

- Una migración de datos crea las 11 filas con los textos actuales.

**Quote** (`quotes`) — cambios

| Campo | Cambio |
|---|---|
| `location` | Char(160), opcional. "Ubicación del espacio" |
| `has_photos` | Bool, por defecto `False`. "Tiene fotos del espacio" |
| `needs_visit` | Bool, por defecto `False`. "No sabe los m²: pide una visita" |
| `estimated_price` | Se conserva: ahora es el **total** de la cotización |
| `area`, `area_other`, `square_meters`, `price_per_m2_snapshot` | **Se eliminan** de `Quote`: pasan a `QuoteItem` |

**QuoteItem** (`quotes`) — nuevo: un renglón por cada área de la cotización

| Campo | Notas |
|---|---|
| `quote` | FK → `Quote`, `on_delete=CASCADE`, `related_name="items"` |
| `area` | FK → `RemodelArea`, `on_delete=PROTECT` |
| `area_other` | Char(120), opcional. Texto cuando el área es "Otro" |
| `square_meters` | Decimal(8,2), opcional. Vacío cuando la persona pidió una visita |
| `price_per_m2_snapshot` | Decimal(10,2), opcional. Precio del área en ese momento |
| `subtotal` | Decimal(12,2), opcional. Vacío = "A cotizar" |

### 2.3 Reglas de negocio (`quotes/services.py`)

Se reutilizan `calculate_estimate`, `format_usd`, `format_square_meters`, `clean_phone`, `area_belongs_to_category` y `build_whatsapp_link`. Cambia y se agrega:

```python
def calculate_total(subtotals) -> Decimal | None:
    """Suma los subtotales. Si falta alguno (None), el total es None: 'A cotizar'."""

def build_whatsapp_message(quote, items, show_estimate: bool) -> str: ...
```

Mensaje nuevo, sin emojis:

```
Hola RP Design, quiero una cotización:

- Nombre: {name}
- Correo: {email}
- Teléfono: {phone}
- Ubicación: {location}                    ← solo si la escribió
- Tipo: {category_name}
- Áreas:
  - Cocina: 10 m² (USD 1.000,00)           ← el monto, solo si se muestra el estimado
  - Baño: 5 m² (USD 400,00)
  - Otro (Terraza): 8 m² (A cotizar)
- Estimado total: USD 1.400,00             ← se omite si show_estimate es False
- Tengo fotos del espacio                  ← solo si marcó la casilla
- No sé los m²: quiero agendar una visita  ← solo si marcó la casilla; las áreas van sin m²

- Mensaje: {message}                       ← solo si lo escribió
```

### 2.4 Migraciones

| App | Migración | Qué hace |
|---|---|---|
| `projects` | `0005_category_is_visible` | Agrega `ProjectCategory.is_visible` |
| `site_content` | `0011_specs_003` | Fuentes, `show_estimate`, `cta_text`, `section` en `Service` y `ProcessStep`, y el modelo `QuoteFormField` |
| `site_content` | `0012_form_fields` (datos) | Crea las 11 filas de `QuoteFormField` con los textos actuales |
| `quotes` | `0006_quote_items` | Crea `QuoteItem`; agrega `location`, `has_photos` y `needs_visit` a `Quote` |
| `quotes` | `0007_migrate_quote_items` (datos) | Por cada cotización existente crea un renglón con su área, m², precio y estimado |
| `quotes` | `0008_remove_single_area_fields` | Elimina de `Quote` los campos que pasaron al renglón |
| `core` | `0004_specs_003_permissions` | Reparte a los grupos los permisos de `QuoteItem` y `QuoteFormField` (`assign_group_permissions`) |

El cambio de la cotización va en tres pasos (tabla nueva → copiar datos → borrar lo viejo), como se hizo con las categorías en specs-001, para no perder información.

### 2.5 API

| Método | Ruta | Cambio |
|---|---|---|
| GET | `/api/project-categories/` | Solo categorías con `is_visible` |
| GET | `/api/projects/?category=<slug>` | Una categoría oculta se trata como inexistente: devuelve todos |
| GET | `/api/projects/` | La tarjeta agrega `description` |
| GET | `/api/quote-categories/` | Solo categorías con `is_visible` |
| GET | `/api/site/` | `settings`: `heading_font`, `body_font`, `show_estimate`. `services`: `cta_text`. `contact`: `form_fields` |
| POST | `/api/quotes/` | Nuevo formato, abajo |

`contact.form_fields` es un objeto indexado por `key`, para que el frontend lo lea directo:

```json
{ "name": { "label": "Nombre", "placeholder": "Tu nombre" },
  "has_photos": { "label": "Tengo fotos del espacio", "placeholder": "" } }
```

**POST `/api/quotes/`**

Petición:
```json
{ "name": "Ana Pérez", "email": "ana@mail.com", "phone": "+58 412-1234567",
  "category": 2,
  "items": [
    { "area": 2, "area_other": "", "square_meters": "10" },
    { "area": 1, "area_other": "", "square_meters": "5" }
  ],
  "location": "Chacao, Caracas", "has_photos": true, "needs_visit": false,
  "message": "", "privacy_accepted": true, "website": "" }
```

Respuesta `201`:
```json
{ "id": 15, "estimated_price": "1400.00", "estimated_price_display": "USD 1.400,00",
  "whatsapp_url": "https://wa.me/584127305964?text=..." }
```

Validación:

| Caso | Respuesta |
|---|---|
| `items` vacío o ausente | `400` en `items`: "Elige al menos un área." |
| Un área no es del tipo (ni común) | `400` en `items`: "Elige un área de la lista." |
| La misma área dos veces | `400` en `items`: "No repitas un área." |
| Área "Otro" sin `area_other` | `400` en `items`: "Especifica qué área quieres remodelar." |
| Sin `needs_visit`: `square_meters` vacío, ≤ 0 o mayor que el máximo | `400` en `items`, con el mismo mensaje de hoy |
| Con `needs_visit`: `square_meters` se ignora y se guarda vacío | — |
| `category` oculta | `400` en `category`: "Elige el tipo de remodelación." |

- Con `show_estimate` apagado, `estimated_price` y `estimated_price_display` van como `null`: el frontend no recibe el monto (CA-30.1). En la base se guarda igual.
- Honeypot, límite de envíos y aceptación de privacidad no cambian.

### 2.6 Panel

| Modelo | Cambios |
|---|---|
| SiteSettings | Bloque nuevo "Tipografía" con las dos fuentes y su ayuda. `show_estimate` en "Calculadora" |
| ProjectCategory | Columna "mostrar en el sitio", editable desde la lista |
| ServicesSection | Campo del texto del botón. Tabla de **servicios** dentro, ordenable arrastrando |
| ProcessSection | Tabla de **pasos** dentro, ordenable arrastrando |
| Service, ProcessStep | Dejan de tener entrada propia en el menú |
| ContactSection | Tabla "Campos del formulario" dentro: sin agregar ni borrar, `key` en solo lectura |
| Quote | Tabla de renglones (área, m², precio usado, subtotal) en solo lectura. Muestra ubicación, fotos y visita. La lista muestra el total |

- Las tablas dentro de una sección usan `SortableInlineAdminMixin`, el mismo patrón de `ProjectMediaInline` (`backend/projects/admin.py`) y `LegalSectionInline`.
- `SingletonAdmin` pasa a heredar de `SortableAdminBase`, que es lo que `django-admin-sortable2` exige al formulario que contiene una tabla ordenable.

### 2.7 Tests del backend

| Qué | Dónde |
|---|---|
| Fuentes: cada formato válido, archivo falso, extensión no permitida, tamaño | `core/tests/test_validators.py` |
| Categoría oculta en `/api/project-categories/`, `/api/quote-categories/` y `?category=` | `projects/tests/test_api.py`, `quotes/tests/test_api.py` |
| `description` en la tarjeta | `projects/tests/test_api.py` |
| `calculate_total`: suma, con un `None`, lista vacía | `quotes/tests/test_services.py` |
| Mensaje: varios renglones, sin emojis, con y sin estimado, con visita, con fotos, con ubicación | `quotes/tests/test_services.py` |
| `POST`: dos áreas y su suma; área de otro tipo; repetida; sin áreas; "Otro" sin texto; con visita sin m²; sin visita y sin m² | `quotes/tests/test_api.py` |
| `show_estimate` apagado: respuesta sin monto, mensaje sin estimado, cotización con estimado guardado | `quotes/tests/test_api.py` |
| Migración: una cotización antigua queda con un renglón equivalente | `quotes/tests/test_migrations.py` |
| `/api/site/`: fuentes, `show_estimate`, `cta_text`, `form_fields` con las 11 claves | `site_content/tests/test_api.py` |
| Panel: pasos y servicios dentro de su sección; campos del formulario sin agregar ni borrar | `site_content/tests/test_admin.py` |
| Roles: permisos de los modelos nuevos | `core/tests/test_roles.py` |

---

## 3. Frontend

### 3.1 Estructura (solo lo que cambia)

```
frontend/src/
├── hooks/useCustomFonts.js          nuevo: registra las fuentes del panel
├── hooks/useSlideshow.js            admite una portada que avanza al terminar su video
├── components/
│   ├── layout/Layout.jsx            usa useCustomFonts
│   ├── layout/Footer.jsx            iconos de WhatsApp, correo e Instagram
│   ├── layout/SocialIcons.jsx       nuevo: los tres iconos en SVG
│   ├── home/Hero.jsx                arma la lista de portadas: video + proyectos
│   ├── home/HeroSlides.jsx          dibuja una portada de imagen o de video
│   ├── home/Services.jsx            botón "Cotizar" en cada tarjeta
│   ├── home/Contact.jsx             sin datos de contacto
│   ├── home/ContactInfo.*           se borra
│   ├── projects/ProjectCard.jsx     descripción en la capa
│   └── quote/
│       ├── QuoteCalculator.jsx      áreas con casillas, campos nuevos, textos del panel
│       ├── AreaItem.jsx             nuevo: una casilla de área con sus m²
│       ├── SquareMetersSlider.jsx   campo numérico + barra, sincronizados
│       ├── EstimateDisplay.jsx      total de varios renglones
│       └── QuoteSuccess.jsx         sin monto si el estimado está oculto
├── pages/HomePage.jsx               Proceso antes que Servicios
├── pages/ProjectsPage.jsx           título de la sección
└── utils/
    ├── estimate.js                  + calculateTotal()
    └── quoteValidation.js           valida renglones y campos nuevos
```

### 3.2 Fuentes del panel (RF-19)

`useCustomFonts(settings)`, llamado desde `Layout` junto a `useAccentColor` y `useFavicon`:

```js
// Por cada fuente cargada en el panel:
const font = new FontFace('RP Títulos', `url(${settings.heading_font})`, { display: 'swap' })
await font.load()
document.fonts.add(font)
document.documentElement.style.setProperty('--font-display', "'RP Títulos', 'Archivo Narrow', sans-serif")
```

- La variable CSS solo se cambia **después** de que la fuente cargó. Si falla, el sitio se queda con la original (RF-19.5).
- La fuente original queda siempre como respaldo en la lista (`'RP Títulos', 'Archivo Narrow', sans-serif`).
- Las fuentes Archivo siguen incluidas en el sitio: son el respaldo y lo que se ve mientras llega la del panel.

### 3.3 Hero con video (RF-26)

- `Hero` arma una sola lista de portadas:
  ```js
  const slides = [
    ...(showVideo ? [{ type: 'video', key: 'video', src: hero.video, poster: hero.image }] : []),
    ...projects.map((project) => ({ type: 'project', key: project.slug, project })),
  ]
  ```
- `showVideo` es `false` con "reducir movimiento". En ese caso, si hay imagen de respaldo y ningún proyecto, se muestra la imagen como hoy.
- `HeroSlides` dibuja `<video muted playsInline>` para la portada de video e `<img>` para las de proyecto.
- **Avance:** `useSlideshow` recibe `isTimed` (¿la portada activa avanza con el temporizador?). Para el video es `false`: avanza cuando el video dispara `ended`, llamando a `next()`.
- **Al activarse**, el video vuelve a `currentTime = 0` y se reproduce; al dejar de ser la portada activa, se pausa.
- **Pausa:** con la rotación detenida (botón, cursor o foco) el video se pausa; al reanudar, sigue.
- **Con una sola portada (solo el video):** se reproduce en bucle, sin controles, como hoy.
- **Barra de progreso:** para el video dura lo que dura el video (`--slide-duration` se pone con su `duration` al cargar los metadatos).
- **Pie del hero:** la portada de video no tiene proyecto, así que no muestra nombre ni enlace; los controles siguen.

### 3.4 Tarjetas de proyecto (RF-22)

- La capa `.project-card__overlay` deja de decir "Ver proyecto" y muestra `project.description`.
- Estilos: `overflow-y: auto` para el scroll interno, `white-space: pre-line` para los saltos de línea, texto alineado arriba y fondo `--color-dark` al 80 % para asegurar el contraste.
- Como hoy, solo aparece dentro de `@media (hover: hover)` y con `:focus-visible`.
- `CategoryCard` (inicio) no cambia: sigue diciendo "Ver proyectos".

> **Nota de accesibilidad:** la capa lleva `aria-hidden`, como hoy. Un lector de pantalla no lee la descripción en la tarjeta (leería un texto largo por cada proyecto de la lista); la lee en la página del proyecto.

### 3.5 Inicio, Servicios y página de proyectos

- `HomePage`: `<Hero /> <ProjectCategories /> <Process /> <Services /> <Contact>`.
- `Services`: cada tarjeta agrega un `<Button to="/#contacto" size="small">` con `services.cta_text`.
  - Va al final de la tarjeta y **siempre ocupa su espacio**; lo que cambia es su `opacity` (0 → 1). Así la tarjeta no cambia de tamaño (CA-24.1).
  - Visible con `:hover` y `:focus-within` de la tarjeta. Fuera de `@media (hover: hover)` (táctil), `opacity: 1` siempre.
- `ProjectsPage`: `PAGE_TITLE` pasa a ser `site.projects_section.title`.

### 3.6 Formulario (RF-27 a RF-32)

Orden de los campos:

```
Nombre · Teléfono · Correo
Tipo de remodelación · Ubicación del espacio
Áreas a remodelar
   ☑ Cocina     [ 10 ] m²  ────●──────   USD 1.000,00
   ☑ Baño       [  5 ] m²  ─●─────────   USD 400,00
   ☐ Sala
   ☐ Otro
☐ No sé cuántos m² son, agendar una visita
Estimado total: USD 1.400,00  + nota de precio
Mensaje (opcional)
☐ Tengo fotos del espacio
☐ Acepto la política de privacidad…
[ Enviar por WhatsApp ]
```

**Estado.** Las áreas dejan de ser un valor y pasan a un objeto por área marcada:

```js
// { [idDelArea]: { square_meters: '10', area_other: '' } }
const [items, setItems] = useState({})
```

Marcar una casilla agrega su entrada (con 10 m² de inicio); desmarcarla la quita. Cambiar el tipo vacía `items`.

**`AreaItem`** (una fila por área del tipo elegido):
- Casilla con el nombre del área.
- Marcada, y sin "agendar visita": muestra `SquareMetersSlider` y su subtotal.
- Si es "Otro": además, el campo para especificar.

**`SquareMetersSlider`** (RF-29): un `<input type="text" inputMode="decimal">` y la barra, con el mismo valor.
- Escribir actualiza el valor; la barra muestra ese valor redondeado y acotado a su rango.
- Mover la barra escribe el número entero en el campo.
- Cada fila tiene `id` propios (`quote-area-<id>-m2`) para que etiqueta, campo y error queden unidos.

**Total** (`utils/estimate.js`):

```js
/** Suma de subtotales. Si alguno es null, el total es null ("A cotizar"). */
export function calculateTotal(subtotals)
```

**`EstimateDisplay`**: muestra el total. No se dibuja si `settings.show_estimate` es `false` (tampoco los subtotales ni la nota).

**Casilla de visita** (RF-32.2): marcada, las filas no muestran los m² y el total es "A cotizar".

**Textos** (RF-31): un ayudante lee `contact.form_fields[key]` y, si el título está vacío, usa el texto original:

```js
const text = getFieldText(formFields, 'name')   // { label, placeholder }
```

**Validación** (`utils/quoteValidation.js`): al menos un área; m² válidos en cada área marcada salvo que haya visita; texto en "Otro". Los errores de cada fila se muestran junto a ella.

**Envío:** `items` se convierte en la lista que espera la API, con los m² con punto decimal.

### 3.7 Pie de página y Contacto (RF-33)

- `SocialIcons`: tres enlaces con SVG en línea (WhatsApp, sobre de correo, Instagram). Cada uno con `aria-label` ("Escribir por WhatsApp", "Enviar un correo", "Ver Instagram") y área de 44 × 44 px. Reutiliza `buildWhatsAppLink` (`utils/whatsapp.js`).
- `Footer`: los iconos van en la segunda fila, entre los enlaces legales y el crédito.
- `Contact`: se quita `<ContactInfo />`. Se borran `ContactInfo.jsx` y `ContactInfo.css`.
- El botón flotante de WhatsApp sigue ocultándose mientras la sección Contacto está a la vista; el pie conserva su espacio inferior en móvil para que no tape los iconos.

### 3.8 Tests del frontend

| Qué | Cómo |
|---|---|
| `calculateTotal`: suma, con `null`, vacío | Vitest |
| `validateQuote`: sin áreas, m² por área, "Otro" sin texto, con visita | Vitest |
| Fuente cargada y quitada | Playwright (con una fuente de prueba subida al panel) |
| Categoría oculta en inicio, filtro y formulario | Playwright |
| Capa con la descripción; botón "Cotizar" | Playwright |
| Hero: video + imágenes, avance al terminar, pausa, movimiento reducido | Playwright |
| Formulario: dos áreas, m² a mano, suma, visita, envío real y mensaje sin emojis | Playwright |
| Interruptor de precio apagado | Playwright |
| Pie con iconos; Contacto sin datos | Playwright |
| Cuatro páginas a 360, 768, 1280 y 1920 px, sin scroll horizontal | Playwright |

---

## 4. Registro de decisiones

| # | Decisión | Motivo |
|---|---|---|
| D-45 | Las fuentes se validan por sus primeros bytes | Mismo criterio que imágenes y videos: la extensión sola no prueba nada |
| D-46 | La fuente se aplica solo cuando terminó de cargar | Si falla, el sitio sigue legible con la original |
| D-47 | Pasos y servicios se relacionan con su sección | Es lo que permite editarlos dentro del formulario de la sección |
| D-48 | La cotización pasa a tener renglones (`QuoteItem`) | Varias áreas, cada una con sus m², su precio y su subtotal |
| D-49 | El total es "A cotizar" si a alguna área le falta precio | Un total parcial se leería como el precio completo |
| D-50 | Mensaje de WhatsApp en texto simple, con guiones | Los emojis llegaban como "?" en algunas versiones de WhatsApp |
| D-51 | Con el estimado oculto, la API no envía el monto | Si viajara, cualquiera podría verlo en el navegador aunque no se muestre |
| D-52 | Los textos del formulario son filas fijas, identificadas por `key` | El código necesita saber qué campo es cada uno; el cliente solo cambia textos |
| D-53 | El video del hero avanza con su evento `ended` | Su duración la define el archivo, no el temporizador de 6 s |
| D-54 | El botón "Cotizar" reserva su espacio y cambia de opacidad | La tarjeta no cambia de tamaño al aparecer |

## 5. Riesgos

| Riesgo | Cómo se atiende |
|---|---|
| El formulario se alarga y baja la cantidad de envíos | Lo opcional se marca como tal; las filas de m² solo aparecen en las áreas marcadas |
| La migración de cotizaciones pierde datos | Tres pasos, con un test que compara antes y después |
| Fuente del cliente pesada o con un solo grosor | Límite de 2 MB y ayuda en el panel; el sitio nunca queda sin texto |
| Video largo en el hero retrasa las imágenes | El panel ya pide subirlo corto y comprimido; anterior y siguiente permiten saltarlo |
| Descripción larga con scroll dentro de la tarjeta resulta incómoda | Es la decisión P-23; la alternativa (recortar) queda anotada |
| Cambia el formato de `POST /api/quotes/` | El único consumidor es el frontend, que se cambia a la vez; aún no hay despliegue |
