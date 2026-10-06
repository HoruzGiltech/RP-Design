# Diseño técnico — Web RP Design

> **Cómo** se construye lo que pide `requirements.md`.
> Cada decisión lleva su motivo. Si algo cambia, se actualiza aquí antes de programarlo.

**Estado:** Aprobado (v3, 2026-10-05) — incluye §3.6 Animaciones y el video de la Portada

---

## 1. Arquitectura

```
 Visitante ──► React (Vite)  ──fetch JSON──►  Django + DRF  ──►  PostgreSQL
                                                   │
 Cliente  ──► Django Admin (/<ADMIN_URL>/) ────────┤
                                                   └──►  Archivos: disco local (dev) / Cloudflare R2 (prod)

 Formulario ──► POST /api/quotes/ ──► guarda la cotización y devuelve el enlace wa.me ──► WhatsApp
```

- **Frontend** y **backend** son proyectos separados que se comunican solo por la API.
- La **API pública es de solo lectura**, salvo `POST /api/quotes/`.
- La lógica importante (calcular el precio y armar el mensaje) vive **en el backend**. El frontend repite el cálculo solo para mostrar el estimado en vivo.

---

## 2. Backend (Django)

### 2.1 Apps

| App | Responsabilidad |
|---|---|
| `core` | Clases base (`SingletonModel`, `OrderedModel`), validadores de archivos, procesamiento de imágenes, nombres de archivos subidos, grupos y permisos |
| `projects` | Proyectos y su multimedia |
| `quotes` | Áreas, precios y cotizaciones; cálculo y enlace de WhatsApp |
| `site_content` | Configuración general y secciones editables del sitio |

### 2.2 Clases base (`core`)

```python
class TimeStampedModel(models.Model):     # created_at, updated_at
class OrderedModel(models.Model):         # order (PositiveIntegerField), Meta.ordering = ["order"]
class VisibleModel(models.Model):         # is_visible (bool, default True) → "Mostrar en el sitio"
class SingletonModel(models.Model):
    # Siempre pk=1. save() fuerza pk=1, delete() no hace nada.
    # load() devuelve el registro y lo crea si no existe.
```

> **Decisión:** el `SingletonModel` es propio (unas 15 líneas) en lugar de usar `django-solo`, para no sumar una dependencia por algo tan simple.

### 2.3 Modelos

#### `projects`

**Project** (`TimeStampedModel`, `OrderedModel`)

| Campo | Tipo | Notas |
|---|---|---|
| `title` | Char(150) | Obligatorio |
| `slug` | Slug, único | Se genera desde el título y se puede editar |
| `summary` | Char(300) | Texto corto para la tarjeta |
| `description` | Text | Detalle |
| `category` | Char(80), opcional | Etiqueta de la tarjeta, ej. "Fachada · Residencial" (se muestra en mayúsculas, como en la maqueta) |
| `location` | Char(120), opcional | |
| `year` | PositiveSmallInteger, opcional | |
| `cover_image` | Image | Obligatoria; se procesa (§2.5) |
| `cover_thumbnail` | Image | Se genera sola; no se edita |
| `cover_alt` | Char(150) | |
| `is_published` | Bool | Por defecto `False` |
| `is_featured` | Bool | Máximo 3, se valida en `clean()` |
| `featured_order` | PositiveSmallInteger | Orden entre los destacados |

**ProjectMedia** (`OrderedModel`)

| Campo | Tipo | Notas |
|---|---|---|
| `project` | FK → Project | `on_delete=CASCADE`, `related_name="media"` |
| `media_type` | Choice | `image` / `video` (se detecta del archivo) |
| `file` | File | Se valida (§2.6) |
| `thumbnail` | Image | Solo para imágenes; se genera sola |
| `poster` | Image, opcional | Solo para videos |
| `alt_text` | Char(150) | |

#### `quotes`

**RemodelArea** (`OrderedModel`)

| Campo | Tipo | Notas |
|---|---|---|
| `name` | Char(60) | Baño, Cocina, Sala, Patio, Piscina, Otro |
| `slug` | Slug, único | |
| `price_per_m2` | Decimal(10,2), opcional | En USD. Vacío → "A cotizar" |
| `is_other` | Bool | Si es `True`, pide el campo de texto "especifique" |
| `is_active` | Bool | |

Las 6 áreas iniciales se crean con una **migración de datos**, sin precio.

**Quote** (`TimeStampedModel`)

| Campo | Tipo | Notas |
|---|---|---|
| `name` | Char(120) | |
| `email` | Email | |
| `phone` | Char(30) | Se guarda limpio: solo `+` y dígitos |
| `area` | FK → RemodelArea | `on_delete=PROTECT` |
| `area_other` | Char(120), opcional | Obligatorio si `area.is_other` |
| `square_meters` | Decimal(8,2) | |
| `price_per_m2_snapshot` | Decimal(10,2), opcional | Precio usado en ese momento (el de configuración puede cambiar) |
| `estimated_price` | Decimal(12,2), opcional | `None` = "A cotizar" |
| `message` | Text, opcional | Máx. 1000 caracteres |
| `whatsapp_message` | Text | Texto exacto que se envió |
| `status` | Choice | `new` / `contacted` / `closed`; por defecto `new` |

> **Decisión:** se guarda una copia del precio por m² (`price_per_m2_snapshot`) para que las cotizaciones viejas no cambien de valor cuando el cliente actualice sus precios.

#### `site_content`

Cada modelo corresponde a una sección del inventario (`requirements.md` §3). Entre paréntesis va el valor inicial, tomado de la maqueta.

**SiteSettings** (`SingletonModel`): marca, contacto y configuración general (S1, S7, S8)

| Campo | Valor inicial / notas |
|---|---|
| `brand_initials` | "RP" (se usan en el círculo si no hay logo) |
| `brand_name` | "RP DISEÑO" |
| `brand_subtitle` | "INTERIOR · ARQUITECTURA" |
| `logo` | Image, opcional |
| `header_cta_text` | "Cotiza tu proyecto" |
| `accent_color` | Choice: `#111111` Negro (por defecto), `#8A5A3B` Terracota, `#3E4A3D` Verde oliva, `#5B6670` Pizarra. Son las 4 opciones que trae la maqueta |
| `whatsapp_number` | "584127305964". Formato internacional, sin `+` ni espacios; se valida |
| `whatsapp_display` | "0412 730 5964" (cómo se muestra el número en el sitio) |
| `contact_email` | "rpdesings05@gmail.com" (confirmado por el cliente) |
| `instagram_handle` | "rpdesign_ve" (la URL se arma sola) |
| `city` | "Caracas, Venezuela" |
| `price_note` | Ver el texto abajo |
| `max_square_meters` | Decimal, `10000` |

Texto inicial de `price_note`:
> Precio referencial en USD, sujeto a modificación tras visita técnica. También puede pagarse en bolívares a tasa BCV del día.

**Secciones únicas** (`SingletonModel` + `VisibleModel`):

| Modelo | Sección | Campos (valor inicial) |
|---|---|---|
| `HeroSection` | S2 | `eyebrow` ("ESTUDIO DE DISEÑO DE INTERIORES · CARACAS"), `title` ("Transformamos tus espacios, del plano a la obra."), `body`, `primary_cta_text` ("Agenda una visita" → `#contacto`), `secondary_cta_text` ("Ver proyectos" → `#proyectos`), `image` (opcional), `image_alt`, `video` (opcional, `mp4`/`webm`, mismas validaciones de §2.6; RF-06.5) |
| `ServicesSection` | S4 | `title` ("Un solo equipo para todo tu proyecto"), `intro` |
| `ProjectsSection` | S5 | `title` ("Proyectos recientes"), `instagram_link_text` ("Ver más en Instagram"), `view_all_text` ("Ver todos los proyectos") |
| `ProcessSection` | S6 | `title` ("Ve tu espacio antes de construirlo"), `intro`, `video` (opcional), `video_poster` (opcional) |
| `ContactSection` | S7 | `title` ("Cuéntanos sobre tu espacio"), `intro` ("Te respondemos con los próximos pasos…"), `submit_text` ("Enviar por WhatsApp") |
| `FooterSection` | S8 | `name` ("RP DISEÑO INTERIOR"), `tagline` ("Arquitectura · Interiorismo · Remodelaciones — Caracas") |
| `SeoSettings` | S9 | `site_title` ("RP Diseño Interior"), `meta_description` (vacía al inicio: la maqueta no trae una), `share_image` (no tiene `is_visible`) |

**Listas** (`OrderedModel` + `VisibleModel`):

| Modelo | Sección | Campos | Datos iniciales |
|---|---|---|---|
| `Specialty` | S3 | `text` | Diseño residencial, Diseño comercial, Renders 3D, Ejecución de obra |
| `Service` | S4 | `title`, `description` | Levantamiento de espacio, Proyecto de diseño, Ejecución de obra (con los textos de la maqueta) |
| `ProcessStep` | S6 | `title`, `description` | Renders 3D, Video recorridos, Planimetría, Ejecución de obra (con los textos de la maqueta) |

- El número de cada servicio (01, 02…) y la letra de cada paso (A, B…) **no se guardan**: el frontend los calcula según su posición entre los elementos visibles. Así, al reordenar u ocultar uno, no hay que renumerar a mano.
- Una **migración de datos** carga todos los textos y datos de contacto de la maqueta. Así el sitio se ve igual que la maqueta desde el primer arranque (CA-05.3), y el cliente solo tiene que subir sus fotos.

### 2.4 Reglas de negocio (`quotes/services.py`)

Todo en funciones puras, fáciles de probar:

```python
def calculate_estimate(area: RemodelArea, square_meters: Decimal) -> Decimal | None:
    """None si el área no tiene precio (se muestra 'A cotizar')."""
    if area.price_per_m2 is None:
        return None
    return (area.price_per_m2 * square_meters).quantize(Decimal("0.01"))

def format_usd(amount: Decimal | None) -> str:
    """Decimal('1250.5') -> 'USD 1.250,50'; None -> 'A cotizar'."""

def format_square_meters(square_meters: Decimal) -> str:
    """Decimal('12.50') -> '12,5'; Decimal('30.00') -> '30'."""

def clean_phone(phone: str) -> str:
    """'+58 412-123 45 67' -> '+584121234567'."""

def build_whatsapp_message(quote: Quote) -> str: ...

def build_whatsapp_link(phone: str, message: str) -> str:
    """https://wa.me/<phone>?text=<mensaje codificado>.
    Única función que sabe de WhatsApp. Si mañana se usa la API oficial, se cambia solo esto."""
```

Plantilla del mensaje:

```
Hola RP Design, quiero una cotización:

👤 Nombre: {name}
📧 Correo: {email}
📱 Teléfono: {phone}
🏠 Área: {area}            ← "Otro: {area_other}" si aplica
📐 Metros cuadrados: {m2} m²
💲 Estimado: {estimate}    ← "USD 1.250,00" o "A cotizar"

💬 Mensaje: {message}      ← se omite la línea si está vacío
```

### 2.5 Procesamiento de imágenes (`core/images.py`)

- Se usa Pillow. Se corrige la orientación EXIF y se eliminan los metadatos (GPS de las fotos del celular).
- Versión optimizada: lado mayor de **1920 px**, calidad 82.
- Miniatura: lado mayor de **600 px**.
- Se ejecuta en `save()` solo cuando el archivo cambió.

### 2.6 Validación de archivos (`core/validators.py`)

1. **Extensión** en la lista permitida.
2. **Tamaño** ≤ `MAX_IMAGE_MB` / `MAX_VIDEO_MB` (de `.env`).
3. **Contenido real**: imágenes con `Pillow.Image.verify()`; videos leyendo los primeros bytes con la librería `filetype`.
4. **Renombrado** (`core/uploads.py`, función `build_unique_path`): `projects/<año>/<uuid>.<ext>`. Nunca se usa el nombre original.

> **Decisión:** se eligió `filetype` (Python puro) en lugar de `python-magic`, porque esta última necesita instalar `libmagic` en el sistema y complica Docker y Railway.

### 2.7 API (Django REST Framework)

Base: `/api/`. Solo JSON. Todas las URLs de archivos son absolutas.

| Método | Ruta | Descripción | Throttle |
|---|---|---|---|
| GET | `/api/site/` | Todo el contenido del sitio en **una sola llamada**: `settings`, `hero`, `specialties[]`, `services` (con `items[]`), `projects_section`, `process` (con `steps[]`), `contact`, `footer`, `seo` | `public` |
| GET | `/api/projects/` | Proyectos publicados (tarjeta: slug, title, summary, category, cover_thumbnail, cover_alt). Acepta `?featured=true` | `public` |
| GET | `/api/projects/<slug>/` | Detalle con `media[]` ordenada | `public` |
| GET | `/api/quote-areas/` | Áreas activas: `id`, `name`, `price_per_m2`, `is_other` | `public` |
| POST | `/api/quotes/` | Crea la cotización | `quotes` |

**POST `/api/quotes/`**

Petición:
```json
{ "name": "Ana Pérez", "email": "ana@mail.com", "phone": "+58 412-1234567",
  "area": 2, "area_other": "", "square_meters": "12.5", "message": "",
  "website": "" }
```
Respuesta `201`:
```json
{ "id": 15, "estimated_price": "1250.00", "estimated_price_display": "USD 1.250,00",
  "whatsapp_url": "https://wa.me/584121234567?text=..." }
```
Respuesta `400`: `{ "campo": ["mensaje en español"] }`. Respuesta `429`: límite de envíos alcanzado.

- `website` es el **honeypot**: si viene con algo, se responde `201` con un enlace falso y **no se guarda nada**. Así el bot no sabe que fue detectado.
- Si se envía `estimated_price` en la petición, se ignora.

Los dos throttles, `public: 120/min` y `quotes: 5/hour`, se configuran en `REST_FRAMEWORK` y se pueden cambiar desde `.env`.

- En `/api/site/`, las secciones ocultas llegan con `is_visible: false`; de las listas solo llegan los elementos visibles, ya ordenados.
- El honeypot se revisa **antes** de validar: un bot con datos inválidos también recibe el `201` falso.
- Los contadores de límite viven en la memoria del proceso. Con varios procesos de `gunicorn` en producción hará falta una caché compartida, y `NUM_PROXIES` para leer la IP real detrás de Cloudflare (fase 5).

### 2.8 Panel (Django Admin)

| Modelo | Configuración |
|---|---|
| Project | `SortableAdminMixin` para ordenar la lista; `ProjectMediaInline` ordenable (`SortableInlineAdminMixin`); vista previa de la miniatura; filtros `is_published` e `is_featured`; `prepopulated_fields` para el slug |
| RemodelArea | Lista editable (`list_editable = price_per_m2, is_active`) y ordenable |
| Quote | Solo lectura salvo `status`; filtros por estado, área y fecha; búsqueda por nombre, correo y teléfono; enlace "Abrir WhatsApp" con el cliente |
| Singletons | Sin botón "Agregar" ni "Eliminar"; desde el menú se entra directo al formulario de edición |
| Specialty, Service, ProcessStep | Ordenables y con `is_visible` en la lista. Cada lista tiene su propia entrada en el menú del panel |

- Interfaz en español (`LANGUAGE_CODE = "es"`), con título "Panel RP Design".
- URL: `/<ADMIN_URL>/`, tomada de `.env`.

### 2.9 Roles y permisos

Una migración de datos (`core/migrations/000X_create_groups.py`) crea:

| Grupo | Permisos |
|---|---|
| **Admin** | `add`, `change`, `delete` y `view` de todos los modelos de `projects`, `quotes` y `site_content`, más `auth.user` y `auth.group` |
| **Viewer** | Solo `view_*` de los mismos modelos (sin `auth`) |

- Django Admin ya muestra en solo lectura los modelos donde el usuario solo tiene `view`. Así se cumple CA-04.1 sin código extra.
- Los usuarios del panel necesitan `is_staff=True` y su grupo. **No** se usa `is_superuser` para el cliente; el superusuario queda solo para el desarrollador.
- Como los permisos se crean después de las migraciones de cada app, la migración de grupos depende de las últimas migraciones de esas apps y llama a `create_permissions` antes de asignar.
- El rol Admin gestiona usuarios, pero **no puede** marcar "superusuario", dar permisos sueltos ni editar o borrar la cuenta del desarrollador (`core/admin.py`). Sin este control, quien puede editar usuarios podría darse acceso total.
- Si se agrega un modelo nuevo, hace falta otra migración que dé sus permisos a los grupos. Un test (`core/tests/test_roles.py`) falla si se olvida.

### 2.10 Seguridad

| Medida | Implementación |
|---|---|
| Secretos | `django-environ` lee `.env` |
| Fuerza bruta en el login | `django-axes`: 5 fallos → 30 min de bloqueo. Se bloquea la IP, no el usuario, para que nadie pueda dejar al cliente fuera del panel. Página de bloqueo propia, en español |
| CORS | `django-cors-headers`, con `CORS_ALLOWED_ORIGINS` desde `.env` |
| CSRF | Activo en el admin. La API pública no usa cookies, así que el POST de cotizaciones no necesita CSRF |
| Producción | `DEBUG=False`, `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, HSTS (un año, con subdominios), `SECURE_PROXY_SSL_HEADER` y `CSRF_TRUSTED_ORIGINS` desde `.env`. Con `DEBUG=False` el backend no arranca si `DJANGO_SECRET_KEY` sigue con el valor de ejemplo |
| Archivos estáticos | `whitenoise` sirve los estáticos del admin |
| Contraseñas | Validadores de Django activos (mín. 10 caracteres) |

### 2.11 Almacenamiento de archivos

- `USE_R2=False` (local): se guardan en `MEDIA_ROOT` en disco.
- `USE_R2=True` (producción): `django-storages` con el backend S3 apuntando a Cloudflare R2.

### 2.12 Variables de entorno (`.env.example`)

```bash
# Django
DJANGO_SECRET_KEY=cambia-esto
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
ADMIN_URL=panel-rp/
FRONTEND_URL=http://localhost:5173
CORS_ALLOWED_ORIGINS=http://localhost:5173

# Solo en producción
CSRF_TRUSTED_ORIGINS=
SECURE_HSTS_SECONDS=31536000

# Base de datos (los POSTGRES_* crean la base en Docker; DATABASE_URL la usa Django)
POSTGRES_USER=rp
POSTGRES_PASSWORD=rp
POSTGRES_DB=rpdesign
DATABASE_URL=postgres://rp:rp@db:5432/rpdesign

# Límites
MAX_IMAGE_MB=5
MAX_VIDEO_MB=50
THROTTLE_PUBLIC=120/min
THROTTLE_QUOTES=5/hour

# Almacenamiento (producción)
USE_R2=False
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=
R2_PUBLIC_URL=

# Frontend (archivo frontend/.env — todo lo que empieza con VITE_ es PÚBLICO)
VITE_API_URL=http://localhost:8000/api
```

### 2.13 Dependencias del backend

`Django` (5.2 LTS, ver D-22), `djangorestframework`, `psycopg[binary]`, `django-environ`, `django-cors-headers`, `django-axes`, `django-admin-sortable2`, `django-storages[s3]`, `Pillow`, `filetype`, `whitenoise`, `gunicorn`.

---

## 3. Frontend (React + Vite)

### 3.0 Design tokens (extraídos de la maqueta)

La maqueta usa estilos en línea. Estos son sus valores, que van a `styles/tokens.css` como variables CSS. **Ningún componente usa colores ni tamaños sueltos**: todo sale de estas variables.

**Colores**

| Variable | Valor | Uso en la maqueta |
|---|---|---|
| `--color-bg` | `#F4F3F0` | Fondo general, tarjetas de servicios, caja del formulario |
| `--color-bg-alt` | `#E8E6E1` | Fondo de la sección Contacto |
| `--color-placeholder` | `#DEDBD5` | Recuadro de media sobre fondo claro |
| `--color-border` | `#D6D3CD` | Bordes y líneas divisorias |
| `--color-border-input` | `#A8A59E` | Borde de los inputs |
| `--color-text` | `#111111` | Texto principal y líneas fuertes (lista de Proceso) |
| `--color-text-secondary` | `#3A3935` | Párrafos |
| `--color-text-muted` | `#5A5853` | Antetítulos y subtítulo del logo |
| `--color-link-hover` | `#555555` | Hover de enlaces |
| `--color-dark` | `#111111` | Fondo de Proyectos y del pie de página |
| `--color-dark-surface` | `#2B2A28` | Recuadro de media sobre fondo oscuro |
| `--color-on-dark` | `#F4F3F0` | Títulos sobre fondo oscuro |
| `--color-on-dark-secondary` | `#C9C6BF` | Párrafos sobre fondo oscuro |
| `--color-on-dark-muted` | `#A8A59E` | Categorías y pie de página |
| `--color-white` | `#FFFFFF` | Fondo de inputs y texto de botones |
| `--color-accent` | `#111111` (por defecto) | Botón principal, botón de envío y números de Servicios. **Se sobrescribe con `settings.accent_color`** desde la API |

**Tipografía**: Archivo (400, 500, 600, 800) para el texto y Archivo Narrow (500, 700) para los títulos, los números y la franja.

| Variable / estilo | Valor |
|---|---|
| `--font-body` | `'Archivo', system-ui, sans-serif` |
| `--font-display` | `'Archivo Narrow', sans-serif` |
| H1 (Hero) | display 700, `clamp(48px, 7vw, 92px)`, line-height 0.95, letter-spacing -2px |
| H2 (secciones) | display 700, `clamp(36px, 5vw, 60px)`, line-height 1, letter-spacing -1px |
| H3 tarjetas | body 600, 22–24px |
| Número de servicio | display 700, 56px, color de acento |
| Letra de proceso | display 700, 20px |
| Franja | display 500, 20px |
| Párrafo grande / normal | 17–18px / 16px, line-height 1.6 |
| Antetítulo / categoría | 13px, letter-spacing 2–3px, MAYÚSCULAS |
| Menú | 15px |
| Etiquetas del formulario | 14px, 600 |

**Espaciado y layout**

| Variable | Valor |
|---|---|
| `--container-max` | `1240px` |
| `--gutter` | `24px` (padding lateral) |
| `--section-py` | `112px` (Servicios, Proyectos, Proceso, Contacto); Hero `72px 24px 56px` |
| Gaps | 12, 16, 24, 28, 32, 48, 56 y 64 px |
| Grillas | `repeat(auto-fit, minmax(Npx, 1fr))` con N = 200 (franja), 280 (servicios), 320 (hero), 340 (proyectos, proceso, contacto) |
| Alturas de media | Hero 520px · tarjeta de proyecto 420px · video de proceso 300px. En móvil se cambian por `aspect-ratio` |

**Estilo de componentes**
- **Sin bordes redondeados ni sombras.** Todo es recto; la única excepción es el círculo del logo (`border-radius: 50%`, 44px).
- Botón principal: fondo de acento, texto blanco, `16px 28px`, 600. Botón secundario: borde de 1px `--color-text`, `15px 28px`.
- Inputs: `padding 14px`, borde de 1px `--color-border-input`, fondo blanco, `font: inherit`.
- La grilla de servicios usa `gap: 1px` sobre un fondo `--color-border` para dibujar las líneas entre tarjetas.
- Encabezado `sticky`, con borde inferior de 1px.

**Movimiento** (no vienen de la maqueta, que es estática; ver §3.6)

| Variable | Valor | Uso |
|---|---|---|
| `--ease-out` | `cubic-bezier(0.23, 1, 0.32, 1)` | Todas las entradas y los hover. Nunca `ease-in` |
| `--motion-fast` | `160ms` | Pulsación de botones |
| `--motion-hover` | `200ms` | Hover de enlaces, botones y capa de las tarjetas |
| `--motion-reveal` | `500ms` | Entrada de elementos al aparecer en pantalla |
| `--motion-stagger` | `80ms` | Retraso entre un elemento y el siguiente |
| `--reveal-distance` | `24px` | Recorrido de la entrada |
| `--marquee-duration` | `30s` | Una vuelta de la cinta de especialidades |

> **Decisión:** las fuentes se incluyen con `@fontsource/archivo` y `@fontsource/archivo-narrow` (en el propio sitio) en lugar de pedirlas a Google Fonts. Así se ahorra una conexión externa y no se depende de un tercero.

### 3.1 Rutas (React Router)

| Ruta | Página |
|---|---|
| `/` | `HomePage`: Hero, SpecialtiesStrip, Services, FeaturedProjects, Process y Contact (con la calculadora) |
| `/proyectos` | `ProjectsPage`: cuadrícula completa |
| `/proyectos/:slug` | `ProjectDetailPage` |
| `*` | `NotFoundPage` |

Los enlaces del menú a secciones del inicio usan anclas (`/#servicios`).

### 3.2 Estructura

```
frontend/src/
├── api/client.js            # fetch base con VITE_API_URL y manejo de errores
├── api/endpoints.js         # getSite(), getProjects(), getProject(slug), getQuoteAreas(), createQuote()
├── context/SiteContext.jsx  # carga /api/site/ una vez y lo comparte
├── hooks/useFetch.js        # { data, loading, error }
├── hooks/useReveal.js       # avisa cuando un elemento entra en pantalla (IntersectionObserver)
├── utils/currency.js        # formatUSD() — mismo formato que el backend
├── utils/estimate.js        # calculateEstimate() — solo para mostrar en vivo
├── styles/tokens.css        # colores, tipografías y espaciados de la maqueta
├── styles/motion.css        # clases de entrada, cinta y zoom; regla de prefers-reduced-motion
├── styles/global.css
├── components/
│   ├── layout/   Header, Footer, Layout
│   ├── home/     Hero, SpecialtiesStrip, Services, FeaturedProjects, Process, Contact, ContactInfo
│   ├── projects/ ProjectCard, ProjectGrid, MediaGallery, Lightbox
│   ├── quote/    QuoteCalculator, EstimateDisplay
│   ├── media/    MediaPlaceholder (recuadro gris cuando no hay imagen; variante clara y oscura)
│   └── ui/       Button, Spinner, ErrorMessage, Section, Reveal, Marquee
└── pages/        HomePage, ProjectsPage, ProjectDetailPage, NotFoundPage
```

> **Decisión:** se usa `fetch` + un hook propio (`useFetch`) en lugar de React Query o Axios. Para unas 5 llamadas de solo lectura es suficiente y más fácil de entender. El estado global solo guarda el contenido del sitio (Context API), sin Redux.

### 3.3 Componentes clave

**`QuoteCalculator`**
- Estado del formulario con `useState`. La validación del lado del cliente es solo para dar feedback rápido; la que manda es la del backend.
- Muestra `<EstimateDisplay>` en vivo, con el monto o "A cotizar" y la `price_note`.
- Si se elige un área con `is_other`, aparece el campo "Especifique".
- Incluye el honeypot `website`, oculto con CSS (no con `type="hidden"`), con `tabIndex={-1}` y `autoComplete="off"`.
- Al enviar: deshabilita el botón, hace el POST y luego `window.location.assign(whatsapp_url)`. También muestra una pantalla de éxito con el botón **"Abrir WhatsApp"** como respaldo (CA-03.5).
- Errores `400`: los muestra junto a cada campo. `429`: "Has enviado muchas solicitudes, intenta más tarde o escríbenos directo por WhatsApp".

> **Decisión:** se navega con `location.assign` (misma pestaña) en lugar de `window.open`, porque los navegadores bloquean las ventanas nuevas que se abren después de una petición asíncrona.

**`MediaGallery` + `Lightbox`**
- Las imágenes muestran la miniatura y, al hacer clic, se abren en grande. Se cierra con `Esc` y se navega con las flechas.
- Videos: `<video controls preload="metadata" poster=...>`, sin `autoplay`. Solo el video de la Portada usa `autoplay muted loop playsInline`, sin controles (§3.6).

**SEO por página:** un hook pequeño, `useDocumentTitle`, actualiza `document.title` y la meta descripción. No hace falta una librería.

> **Riesgo conocido:** al ser una SPA, la vista previa al compartir un proyecto en WhatsApp o redes mostrará el título y la imagen generales del sitio, no los de cada proyecto. Si hace falta, se puede resolver más adelante con prerenderizado.

### 3.4 Estados de carga y error

Cada página tiene 3 estados: **cargando** (esqueleto o spinner), **error** (mensaje y botón "Reintentar") y **vacío** (la sección se oculta o muestra un texto amable).

### 3.5 Skills de diseño

El proyecto tiene 5 skills instaladas en `.claude/skills/`. **La maqueta manda**: los tokens de §3.0 (sin bordes redondeados ni sombras, Archivo y Archivo Narrow, paleta fija) no se cambian por sugerencia de una skill. Las skills se usan donde la maqueta no dice nada y para revisar la calidad.

| Skill | Dónde entra | Límite |
|---|---|---|
| `impeccable` | `shape` antes de diseñar lo que no está en la maqueta: `/proyectos`, detalle de proyecto, menú hamburguesa, lightbox y campos nuevos del formulario (T-3.5, T-3.9, T-3.10, T-4.2). `audit` y `polish` en los cierres de fase (T-3.13, T-4.8) | Modo refinamiento, nunca rediseño. Su launcher descarga un binario en el primer uso y trabaja con `PRODUCT.md` y `DESIGN.md`: se pide permiso antes de ejecutarlo o de crear esos archivos |
| `ui-ux-pro-max` | Guías de UX y de React para el formulario, la navegación móvil y los estados de carga, error y vacío (T-3.4, T-3.5, T-4.2, T-4.5) | Se ignoran sus paletas y pares de fuentes |
| `emil-design-eng` | Detalles de interacción: hover y foco de botones y tarjetas, transición del menú móvil y del lightbox, botón deshabilitado al enviar (T-3.4 a T-3.10, T-4.4) | Solo CSS y respetando `prefers-reduced-motion`. Sin librerías de animación |
| `playwright-cli` | Capturas a 360, 768, 1280 y 1920 px contra la maqueta (T-3.13), prueba de punta a punta de la cotización (T-4.7) y revisión con teclado (T-4.8) | Solo contra el entorno local |
| `stop-slop` | Textos que escribe el agente: mensajes de error y validación, ayudas del panel, README y la guía del cliente (T-5.9) | No toca los textos del cliente, que salen de la maqueta o quedan como `[TEXTO PENDIENTE]` |

Si una skill propone algo que cambia la spec (un componente nuevo, una dependencia o un token), primero se actualiza la spec y se avisa.

### 3.6 Animaciones

Referencia: https://sparquitectosve.com/ (hecha con Elementor). El inventario se sacó de su código, no de verla en un navegador: entradas `fadeInUp`, `fadeInRight` y `slideInLeft/Up/Right`, carrusel con avance automático, video de fondo, zoom de fondo ligado al scroll y capa con fundido en la galería. Aquí se reproducen esos efectos con el estilo de la maqueta.

| Requisito | Dónde | Cómo |
|---|---|---|
| RF-06.1 | Antetítulo, título e intro de cada sección | `<Reveal>`: de `opacity: 0; translateY(var(--reveal-distance))` al estado final |
| RF-06.2 | Botones de la Portada | `<Reveal from="right">` con retraso, después del título |
| RF-06.3 | Tarjetas de Servicios, Proyectos y pasos de Proceso | `<Reveal>` con `delay = índice × --motion-stagger`. En Servicios, desde 900 px de ancho: la primera tarjeta entra desde la izquierda, la última desde la derecha y las del medio desde abajo |
| RF-06.4 | Franja de especialidades | `<Marquee>`: la lista se repite dos veces dentro de una pista que se mueve con `@keyframes` (`translateX(0)` → `-50%`). La copia lleva `aria-hidden`. Se pausa con `:hover` y `:focus-within` |
| RF-06.5 | Portada | Si `hero.video` existe: `<video autoplay muted loop playsInline poster={hero.image}>` en el recuadro de la imagen. Si no, la imagen |
| RF-06.6 | Imagen de la Portada y portada del detalle | Animación CSS ligada al scroll (`animation-timeline: view()`), de `scale(1)` a `scale(1.08)`, dentro de un contenedor con `overflow: hidden` |
| RF-06.7 | `ProjectCard` | Capa `--color-dark` al 55 % con "Ver proyecto", que aparece con `opacity` en `:hover` y `:focus-visible`; la foto pasa a `scale(1.04)` |

**Reglas**
- Solo se animan `transform` y `opacity`. Así no hay saltos de diseño ni se recalcula la página (CA-06.6).
- `useReveal` usa `IntersectionObserver` y deja de observar tras la primera aparición (RF-06.8).
- El estado oculto solo se aplica cuando `useReveal` ya está activo. Si el navegador no tiene `IntersectionObserver`, `<Reveal>` muestra el contenido tal cual (CA-06.3).
- `motion.css` termina con `@media (prefers-reduced-motion: reduce)`: sin `transform`, sin cinta y sin zoom. `Hero` consulta la misma preferencia y, si está activa, muestra la imagen en lugar del video (RF-06.9).
- El zoom ligado al scroll va dentro de `@supports (animation-timeline: view())`. Donde no hay soporte (hoy Firefox), la imagen queda fija.
- Los hover van dentro de `@media (hover: hover)` para que en pantallas táctiles no quede la capa pegada tras tocar.
- Botones: `transform: scale(0.97)` en `:active`.
- El video de la Portada se sube ya comprimido y corto. Se carga con `preload="metadata"` y la imagen como `poster`, para que el primer pintado no dependa del video.

> **Decisión:** las animaciones se hacen con CSS y un hook de unas 20 líneas, sin GSAP, AOS, Swiper ni Framer Motion. Son efectos simples y una librería sumaría peso y algo más que aprender.

---

## 4. Entorno local (Docker Compose)

| Servicio | Imagen / base | Puerto |
|---|---|---|
| `db` | `postgres` (versión estable actual) | 5432 |
| `backend` | `python` slim + `runserver` en dev | 8000 |
| `frontend` | `node` LTS + `vite dev` | 5173 |

Hay volúmenes para los datos de Postgres y para `media/`.

---

## 5. Pruebas

| Qué | Cómo |
|---|---|
| Cálculo, formato USD y mensaje de WhatsApp | Tests unitarios de `quotes/services.py` |
| Máximo 3 destacados | Test de modelo |
| Borradores ocultos y 404 | Tests de la API |
| Recalcular el precio e ignorar el del cliente | Test de `POST /api/quotes/` |
| Honeypot | El test verifica que no se guarda nada |
| Rate limit | El test hace 6 POST y espera `429` en el último |
| Validación de archivos | Tests con un archivo falso y uno demasiado grande |
| Roles | Tests: el Viewer recibe 403 al crear, editar o borrar; el Admin puede todo |
| Frontend | `formatUSD` y `calculateEstimate` con Vitest; `npm run lint` y `npm run build` |
| Animaciones | Revisión con Playwright: con `prefers-reduced-motion` emulado todo el contenido es visible; sin él, los elementos terminan en su estado final al bajar la página |

---

## 6. Registro de decisiones

| # | Decisión | Motivo |
|---|---|---|
| D-01 | Django Admin como panel | Viene incluido, es seguro y ya trae permisos por rol |
| D-02 | Rutas en vez de modal para los proyectos | URLs que se pueden compartir y botón "atrás" |
| D-03 | Enlace `wa.me` y guardar el mensaje en BD | Gratis, sin cuenta de Meta; no se pierden contactos |
| D-04 | El backend recalcula el precio | No confiar en datos del navegador |
| D-05 | Copia del precio en cada cotización | El historial no cambia cuando se actualizan los precios |
| D-06 | `SingletonModel` propio | Evita una dependencia para unas 15 líneas |
| D-07 | `filetype` en vez de `python-magic` | No requiere librerías del sistema |
| D-08 | `fetch` + Context, sin React Query ni Redux | Más simple para quien empieza |
| D-09 | `location.assign` para WhatsApp | Evita el bloqueo de ventanas emergentes |
| D-10 | Honeypot con respuesta 201 falsa | El bot no se entera de que fue detectado |
| D-11 | Sin conversión automática a Bs. | La tasa BCV en línea no es confiable; se muestra una nota |
| D-12 | "Área a remodelar" reemplaza a "Tipo de proyecto" de la maqueta | Es el campo que define el precio; tener dos selectores parecidos confunde |
| D-13 | Números y letras calculados por posición | Reordenar u ocultar no obliga a renumerar a mano |
| D-14 | Datos iniciales con los textos de la maqueta | El sitio se ve igual a la maqueta desde el primer arranque |
| D-15 | Color de acento configurable (4 opciones) | La maqueta ya lo prevé como opción del diseño |
| D-16 | Fuentes con `@fontsource` | Sin dependencia de Google Fonts |
| D-17 | Animaciones tomadas de sparquitectosve.com, con el aspecto de la maqueta | La maqueta es estática; la referencia aporta el movimiento |
| D-18 | Animaciones con CSS e `IntersectionObserver`, sin librerías | Efectos simples; menos peso y menos dependencias |
| D-19 | No se adoptan las tarjetas que se voltean ni el video de fondo en Contacto | Esconden contenido, fallan en táctil o bajan el contraste del formulario |
| D-20 | La franja de especialidades pasa a ser una cinta en movimiento | Es el equivalente del carrusel automático de la referencia; cambia la distribución de la maqueta en S3 |
| D-21 | Video opcional en la Portada, dentro del recuadro de la foto | Equivale al video de fondo de la referencia sin cambiar la distribución de la maqueta |
| D-22 | Django 5.2 LTS en lugar de 6.1 | `django-admin-sortable2` aún no soporta 6.1 (fallaban las acciones de las listas), y la LTS tiene soporte hasta abril de 2028 |
