# Diseño técnico — specs-001

> **Cómo** se construye lo que pide `specs/specs-001/requirements.md`.
> Solo describe lo que cambia. Lo que no aparece aquí sigue como en `specs/design.md`.

**Estado:** Aprobado (v1, 2026-10-06)

---

## 1. Qué se toca

```
backend/projects/       modelo ProjectCategory, cambios en Project, panel, API
backend/site_content/   SiteSettings (WhatsApp), datos de la Portada
backend/core/           migración de permisos para el modelo nuevo
frontend/src/           Hero nuevo, sección de categorías, filtro en /proyectos, botón flotante
```

No se agregan dependencias, ni en el backend ni en el frontend.

---

## 2. Backend

### 2.1 Modelos (`projects`)

**ProjectCategory** (`OrderedModel`) — nuevo

| Campo | Tipo | Notas |
|---|---|---|
| `name` | Char(60), único | "Comercial", "Residencial", "Corporativo" |
| `slug` | Slug, único, no editable | Se genera del nombre al crear, sin la palabra "proyecto" (RF-10.5) |

- Datos iniciales por migración: las tres categorías, en ese orden.
- No tiene imagen propia: la portada sale de un proyecto (RF-09.7).

**Project** — cambios

| Campo | Cambio |
|---|---|
| `category` | Pasa de `Char(80)` a `FK → ProjectCategory`, `on_delete=PROTECT`, `related_name="projects"`. Obligatorio en el formulario del panel; en la base admite vacío para los proyectos que la migración no pueda asociar |
| `slug` | Deja de ser editable (`editable=False`). Se genera en `save()` cuando está vacío, o sea, solo al crear |
| `show_in_hero` | Bool nuevo, "Mostrar en el hero", por defecto `False` |
| `hero_order` | PositiveSmallInteger nuevo, "Orden en el hero" |
| `is_category_cover` | Bool nuevo, "Usar como portada de su categoría" |
| `is_featured`, `featured_order` | **Se eliminan** (RF-08.10) |

Reglas del modelo:

```python
MAX_HERO_PROJECTS = 6

def clean(self):
    # Sustituye a la validación de los 3 destacados
    if self.show_in_hero and self._count_other_hero_projects() >= MAX_HERO_PROJECTS:
        raise ValidationError({"show_in_hero": "Ya hay 6 proyectos en el hero. Quita uno antes de agregar otro."})

def save(self, *args, **kwargs):
    if not self.slug:
        self.slug = build_project_slug(self.title)   # solo al crear (RF-10.4)
    ...
    super().save(*args, **kwargs)
    if self.is_category_cover:
        # Solo uno por categoría: al marcar este, se desmarca el anterior (RF-09.8)
        Project.objects.filter(category=self.category, is_category_cover=True).exclude(pk=self.pk).update(is_category_cover=False)
```

### 2.2 Dirección web automática (`projects/services.py`, nuevo)

Funciones puras, con tests:

```python
SINGLE_WORD_PREFIX = "proyecto"

def build_base_slug(title: str) -> str:
    """'Remodelación de cocina' -> 'remodelacion-de-cocina'; 'Casa' -> 'proyecto-casa'."""

def make_unique_slug(base_slug: str, existing_slugs) -> str:
    """Si 'proyecto-casa' ya existe -> 'proyecto-casa-2', '-3'..."""

def match_category_name(old_text: str, category_names) -> str | None:
    """'Fachada · Residencial' -> 'Residencial'. La usa la migración de categorías."""
```

- "Una sola palabra" se decide sobre el slug ya limpio: si no contiene ningún guion, se le antepone `proyecto-`.
- Si el título ya es "Proyecto", queda `proyecto` (no `proyecto-proyecto`).
- Un título sin letras ni números (por ejemplo "¿?") da `proyecto`.

### 2.3 Migraciones

| App | Migración | Qué hace |
|---|---|---|
| `projects` | `0002_categories` | Crea `ProjectCategory`. Agrega `category_fk`, `show_in_hero`, `hero_order`, `is_category_cover` |
| `projects` | `0003_migrate_categories` (datos) | Crea las 3 categorías. Para cada proyecto, busca una categoría cuyo nombre aparezca en su texto antiguo (sin distinguir mayúsculas ni tildes): "Fachada · Residencial" → Residencial. Copia `is_featured` → `show_in_hero` y `featured_order` → `hero_order`, para no perder lo que el cliente ya eligió |
| `projects` | `0004_remove_old_fields` | Elimina el `category` de texto, `is_featured` y `featured_order`; renombra `category_fk` → `category`; `slug` pasa a no editable |
| `site_content` | `0006_whatsapp_floating_button` | Elimina `whatsapp_display`. Agrega `whatsapp_greeting` y `show_whatsapp_button` |
| `site_content` | `0007_hero_texts` (datos) | Vacía el título de la Portada y cambia el botón a "Agenda una reunión", **solo si siguen con el texto original** (si el cliente ya los cambió, se respetan) |
| `site_content` | `0008_projects_section_title` (datos) | Cambia el título de la sección Proyectos a "Mis Proyectos", solo si sigue con el texto original |
| `core` | `0003_category_permissions` | Reparte los permisos de `ProjectCategory` a los grupos (`assign_group_permissions`) |

El cambio de `category` se hace en tres pasos (campo nuevo → copiar datos → borrar el viejo) para no perder información por el camino.

### 2.4 `SiteSettings` (`site_content`)

| Campo | Cambio |
|---|---|
| `whatsapp_display` | **Se elimina** (RF-11.2) |
| `whatsapp_greeting` | Char(200) nuevo. Por defecto: "Hola! quiero agendar una reunión" |
| `show_whatsapp_button` | Bool nuevo, "Mostrar el botón flotante de WhatsApp", por defecto `True` |

`HeroSection.title` pasa a admitir vacío (`blank=True`). Los demás campos de la Portada no cambian: `image` y `video` quedan como respaldo (RF-08.9).

### 2.5 Formato del número (`site_content/services.py`, nuevo)

```python
def format_whatsapp_number(number: str) -> str:
    """'584127305964' -> '+58 412 730 5964'. Otros países: '+' y los dígitos."""
```

- Venezuela (empieza por `58` y tiene 12 dígitos): `+58 XXX XXX XXXX`.
- Cualquier otro: `+<dígitos>`, sin agrupar (RF-11.3).

### 2.6 API

| Método | Ruta | Cambio |
|---|---|---|
| GET | `/api/projects/?hero=true` | **Nuevo filtro**, sustituye a `?featured=true`. Proyectos publicados con `show_in_hero`, por `hero_order`. Máximo 6 |
| GET | `/api/projects/?category=<slug>` | **Nuevo filtro.** Si el slug no existe, devuelve todos (CA-09.4) |
| GET | `/api/project-categories/` | **Nuevo.** Categorías con al menos un proyecto publicado, en su orden |
| GET | `/api/projects/` y `/api/projects/<slug>/` | `category` pasa de texto a objeto `{ "name", "slug" }` o `null`. La tarjeta agrega `cover_image` (el hero necesita la imagen grande) |
| GET | `/api/site/` | En `settings`: `whatsapp_display` ahora se **calcula** (2.5); se agregan `whatsapp_greeting` y `show_whatsapp_button` |

Respuesta de `/api/project-categories/`:

```json
[
  { "name": "Residencial", "slug": "residencial", "project_count": 4,
    "cover_thumbnail": "https://.../abc.jpg", "cover_alt": "Sala terminada" }
]
```

- `cover_thumbnail` y `cover_alt` salen del proyecto publicado marcado como portada de la categoría; si no hay, del primero publicado según el orden del panel.
- `?featured=true` deja de existir. El frontend es el único consumidor de la API y se cambia a la vez.

### 2.7 Panel

| Modelo | Cambios |
|---|---|
| ProjectCategory | Nuevo en "Proyectos". Lista ordenable arrastrando. Sin campo de dirección web. No se puede eliminar una categoría con proyectos (mensaje claro, no un error técnico) |
| Project | El campo "dirección web" sale del formulario y pasa a verse en solo lectura al editar. `category` es un desplegable obligatorio. El bloque "Publicación" queda: publicado, mostrar en el hero, orden en el hero, usar como portada de su categoría. En la lista: columnas de categoría y "en el hero"; filtros por categoría y por "en el hero" |
| SiteSettings | En "Contacto" desaparece "WhatsApp como se muestra". Bloque nuevo "Botón flotante de WhatsApp": interruptor y mensaje |

### 2.8 Tests del backend

| Qué | Dónde |
|---|---|
| Slug: varias palabras, una sola, repetido, sin letras, no cambia al editar el título | `projects/tests/test_services.py`, `test_models.py` |
| Máximo 6 en el hero; editar uno ya marcado no falla; los borradores cuentan | `test_models.py` |
| Una sola portada por categoría: marcar otra desmarca la anterior | `test_models.py` |
| Migración de categorías: "Fachada · Residencial" → Residencial; texto sin coincidencia → vacío; destacados → hero | Test de migración |
| `?hero=true`: solo publicados, en orden, máximo 6 | `test_api.py` |
| `?category=`: filtra; slug inexistente devuelve todos | `test_api.py` |
| `/api/project-categories/`: oculta las vacías, cuenta solo publicados, elige bien la portada | `test_api.py` |
| `format_whatsapp_number`: Venezuela y otros países | `site_content/tests/test_services.py` |
| `/api/site/` trae el formato calculado y los campos nuevos | `test_api.py` |
| Panel: sin campo de slug; categoría obligatoria; no se borra una categoría con proyectos | `test_admin.py` |
| Roles: permisos de `ProjectCategory` en Admin y Viewer | `core/tests/test_roles.py` (ya falla solo si se olvida) |

Los tests actuales de los 3 destacados se eliminan o se adaptan al hero.

---

## 3. Frontend

### 3.1 Estructura (solo lo que cambia)

```
frontend/src/
├── api/endpoints.js              + getHeroProjects(), getProjectCategories(); getProjects(categorySlug)
│                                 - getFeaturedProjects()
├── hooks/useSlideshow.js         nuevo: qué portada toca y cuándo cambiar
├── components/
│   ├── home/Hero.jsx             se reescribe (RF-08)
│   ├── home/HeroSlides.jsx       nuevo: las portadas, sus controles e indicadores
│   ├── home/ProjectCategories.jsx   nuevo, reemplaza a FeaturedProjects.jsx (que se borra)
│   ├── projects/CategoryCard.jsx    nuevo: tarjeta de categoría (misma apariencia que ProjectCard)
│   ├── projects/CategoryFilter.jsx  nuevo: "Todos" + categorías en /proyectos
│   ├── projects/ProjectCard.jsx     category pasa a ser project.category.name
│   └── layout/WhatsAppButton.jsx    nuevo (RF-12); se monta en Layout
├── pages/ProjectsPage.jsx        lee ?categoria= de la dirección
└── utils/whatsapp.js             nuevo: buildWhatsAppLink(number, message)
```

### 3.2 Hero (RF-08)

Distribución: sección a todo el ancho, fondo `--color-dark`, alto `min(78vh, 760px)` en escritorio y `min(86vh, 640px)` en móvil.

```
┌──────────────────────────────────────────────────────────────┐
│  [portada del proyecto, a sangre, con una capa oscura]        │
│                                                               │
│  ANTETÍTULO                                                   │
│  Título (solo si el cliente escribió uno)                     │
│  Párrafo                                                      │
│  [Agenda una reunión] [Ver proyectos]                         │
│                                                               │
│  RESIDENCIAL                                    ‹  ›   ❚❚      │
│  Nombre del proyecto →                          ▬ ▭ ▭ ▭       │
└──────────────────────────────────────────────────────────────┘
```

- **Capa oscura:** un degradado de `--color-dark` sobre la foto, más denso abajo y a la izquierda, donde va el texto. Garantiza contraste AA sea cual sea la foto.
- **Texto:** los tokens `--color-on-dark*` que ya usa la sección Proyectos. No hacen falta colores nuevos.
- **Botones del hero:** el principal se invierte sobre fondo oscuro (fondo claro, texto oscuro), porque el color de acento por defecto es negro y no se vería.
- **Nombre y categoría del proyecto:** un enlace a `/proyectos/<slug>` en la parte inferior. Cambia junto con la portada.
- **Controles:** anterior, siguiente y pausa, como botones de texto o signo simples sobre fondo oscuro (el mismo estilo que los del visor de imágenes). Indicadores: barras rectas, no puntos redondos.
- **Imágenes:** en la página solo están la portada activa, la que sale y la siguiente, una encima de otra; solo la activa tiene `opacity: 1`. Así las demás fotos grandes no se descargan hasta que les toca. La primera lleva `fetchPriority="high"`.
- **Título principal:** si `hero.title` está vacío, se pone un `<h1>` solo para lectores de pantalla con `seo.site_title` (CA-08.7).

**Rotación** (`useSlideshow`):

```js
// Devuelve la portada activa y las acciones.
const { index, isPlaying, goTo, next, previous, toggle, pause, resume } = useSlideshow(total, intervalMs)
```

- `setInterval` de 6 s (P-5). Solo corre si hay más de una portada, si `isPlaying` es `true` y si la pestaña está visible (`document.visibilityState`).
- Se pausa con `mouseenter` y `focusin` sobre el hero, y se reanuda al salir, salvo que la persona haya pulsado el botón de pausa.
- Con `prefers-reduced-motion`, arranca en pausa.

**Animación** (CSS, en `motion.css`):

| Efecto | Detalle |
|---|---|
| Fundido entre portadas | `opacity` 0 → 1 en 900 ms con `--ease-out` |
| Zoom lento de la portada activa | `transform: scale(1)` → `scale(1.06)` durante lo que dura la portada (6 s), lineal |
| Cambio del nombre del proyecto | Fundido de 300 ms |
| Menos movimiento | Sin fundido, sin zoom y sin rotación automática |

- Solo `transform` y `opacity`, como el resto del sitio.
- La región de las portadas lleva `aria-roledescription="carrusel"` y `aria-live="off"` mientras rota sola; pasa a `polite` cuando la persona usa los controles (CA-08.6).

**Respaldo** (RF-08.9): con 0 proyectos marcados se usa `hero.video` o `hero.image` como fondo fijo dentro de la misma distribución, sin controles ni nombre de proyecto.

### 3.3 Sección de categorías del inicio (RF-09)

- `ProjectCategories` ocupa el lugar de `FeaturedProjects`: misma `Section` oscura con `id="proyectos"`, mismo encabezado (título y enlace a Instagram) y mismo botón "Ver todos los proyectos".
- La cuadrícula muestra una `CategoryCard` por categoría: foto (`cover_thumbnail`), nombre de la categoría como título y debajo "4 proyectos" (o "1 proyecto"). Misma apariencia y mismas animaciones que `ProjectCard` (entrada escalonada, capa al pasar el cursor con "Ver proyectos").
- Cada tarjeta enlaza a `/proyectos?categoria=<slug>`.
- Si la API no devuelve ninguna categoría, la sección no se dibuja (CA-09.2).

**Orden en el inicio (P-8):** en `HomePage.jsx`, `<ProjectCategories />` pasa a ir antes de `<Services />`. No cambia ningún componente por dentro; solo se revisa que el paso de la Franja a la sección oscura de Proyectos, y de esta a Servicios, se vea bien.

**Franja (P-9):** migración de datos `site_content.0009`, igual que la `0008` del título: cambia la `Specialty` cuyo texto sea exactamente "Renders 3D" a "Corporativo". Si no existe (el cliente ya la editó), no hace nada. Al deshacerla no restaura el texto viejo. No toca `ProcessStep`.

### 3.4 Página `/proyectos` (RF-09.4, RF-09.5)

- La categoría va en la dirección como parámetro: `/proyectos?categoria=residencial`. Se lee con `useSearchParams` de React Router.
- `CategoryFilter`: una fila de enlaces ("Todos", "Comercial", "Residencial"…) sobre la cuadrícula. El activo lleva `aria-current="page"` y un subrayado. Son enlaces y no botones, para que cada filtro tenga su dirección y funcione el botón "atrás".
- Título de la página: "Proyectos" con "Todos", o el nombre de la categoría cuando hay filtro. El título de la pestaña cambia igual.
- Una categoría sin proyectos publicados no aparece en el filtro.

> **Decisión:** parámetro en la dirección (`?categoria=`) en lugar de una ruta nueva (`/proyectos/categoria/<slug>`). Se reutiliza la misma página y no hay riesgo de confundirla con `/proyectos/<slug>` de un proyecto.

### 3.5 Botón flotante de WhatsApp (RF-12)

- `WhatsAppButton` se monta una vez en `Layout`, así aparece en todas las páginas.
- Es un enlace: `<a href={buildWhatsAppLink(number, greeting)} target="_blank" rel="noopener noreferrer" aria-label="Escribir por WhatsApp">`.
- Posición: `position: fixed`, a 24 px del borde inferior y derecho (16 px en móvil), sumando `env(safe-area-inset-bottom)` para los celulares con barra de gestos.
- Tamaño: 56 × 56 px. Icono: el logotipo de WhatsApp como SVG en línea, sin librería de iconos.
- Aspecto (P-3): el icono clásico. Círculo con fondo `--color-whatsapp` (`#25D366`, el verde de la marca) y el logotipo en blanco. Es redondo a propósito, como excepción a la regla de la maqueta, para que se reconozca al instante.
- El blanco sobre ese verde no llega al contraste que se le pide a un texto, pero aquí la forma y el color del logotipo son los que lo identifican; además lleva nombre accesible y un borde fino oscuro para separarlo de fondos claros.
- `z-index` por encima del contenido y del encabezado, y **por debajo** del visor de imágenes (`<dialog>` modal).
- Para no tapar contenido (CA-12.3): el botón **se oculta mientras la sección Contacto está a la vista** (`IntersectionObserver`), porque ahí ya están el formulario y el enlace de WhatsApp. Además, el pie de página gana espacio inferior en móvil y los controles del hero se alinean a la izquierda en pantallas angostas.
- Animación: aparece con un fundido al cargar; al pasar el cursor crece a `scale(1.05)`; al pulsar, `scale(0.97)`.
- No se dibuja si `show_whatsapp_button` es `false` o si no hay número.

`utils/whatsapp.js`:

```js
/** https://wa.me/<número>?text=<mensaje codificado>. Sin mensaje, solo el número. */
export function buildWhatsAppLink(number, message)
```

La usan `WhatsAppButton` y `ContactInfo` (que hoy arma el enlace a mano). El enlace de la cotización lo sigue armando el backend.

### 3.6 Otros cambios pequeños

- `ContactInfo`: muestra `settings.whatsapp_display`, que ahora llega en formato internacional (RF-11). No cambia el componente, solo el dato.
- `ProjectCard` y `ProjectDetailPage`: `project.category` pasa de texto a `project.category?.name`.
- `Header`: el enlace "Proyectos" sigue yendo a `/#proyectos` (ahora, la sección de categorías).

### 3.7 Tokens nuevos (`tokens.css`)

| Variable | Valor | Uso |
|---|---|---|
| `--color-whatsapp` | `#25D366` | Fondo del botón flotante (P-3) |
| `--media-hero-max` | `760px` | Alto máximo del hero |
| `--motion-slide` | `900ms` | Fundido entre portadas |
| `--slide-duration` | `6s` | Tiempo de cada portada y de su zoom |

`--media-hero` (520 px) deja de usarse y se quita.

### 3.8 Tests del frontend

| Qué | Cómo |
|---|---|
| `buildWhatsAppLink`: con y sin mensaje, tildes y signos | Vitest |
| Hero con 0, 1 y 3 portadas; pausa; movimiento reducido | Playwright |
| Categorías en el inicio → `/proyectos?categoria=` → filtro → botón atrás | Playwright |
| Botón flotante: enlace, tamaño, no tapa el envío en móvil, no queda sobre el visor | Playwright |
| Las cuatro páginas a 360, 768, 1280 y 1920 px, sin scroll horizontal | Playwright |

---

## 4. Registro de decisiones

| # | Decisión | Motivo |
|---|---|---|
| D-28 | "Mostrar en el hero" reemplaza a "Destacado" | Con las categorías en el inicio, los destacados ya no se muestran en ningún sitio; dos casillas parecidas confunden |
| D-29 | El título de la Portada queda editable y vacío | El cliente quitó la frase; si quiere otra, la escribe sin tocar código |
| D-30 | La portada de una categoría es un proyecto marcado por el cliente, con respaldo en el primero | El cliente decide; y si no decide nada, la sección no queda sin imagen |
| D-31 | `category` pasa a ser una relación, migrada en tres pasos | No se pierde la categoría que ya tenían los proyectos |
| D-32 | La dirección web se genera una vez y no cambia | Los enlaces ya compartidos siguen funcionando |
| D-33 | El formato del WhatsApp se calcula y se elimina el campo manual | Un solo dato en el panel: no pueden quedar distintos el número real y el mostrado |
| D-34 | Filtro por categoría con `?categoria=` | Se reutiliza `/proyectos` y cada filtro tiene dirección propia |
| D-35 | Rotación del hero con un hook propio y CSS, sin librería de carrusel | Es un fundido entre imágenes; una librería sumaría peso para algo simple |
| D-36 | El hero deja de seguir la maqueta | Cambio pedido por el cliente; se conservan los tokens (colores, tipografías, sin bordes redondeados) |

## 5. Riesgos

| Riesgo | Cómo se atiende |
|---|---|
| Portadas con formas o luces muy distintas dejan el texto ilegible | Capa oscura fija sobre todas las fotos; se revisa el contraste con Playwright |
| Seis portadas de 1920 px pesan en móvil | Solo la primera se carga con prioridad; las demás, diferidas. Se mide con Lighthouse antes del despliegue |
| El botón flotante tapa algo en alguna pantalla | Revisión a 360 px en las cuatro páginas y con el formulario abierto |
| La migración de categorías no acierta con un texto antiguo | El proyecto queda sin categoría y el panel la pide al editarlo; hoy solo hay proyectos de prueba |
| El cliente marca 0 proyectos para el hero | Respaldo con la imagen o el video de la Portada (RF-08.9) |
