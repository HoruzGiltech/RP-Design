# Diseño — specs-004

> **Cómo** se construyen los requisitos de `specs/specs-004/requirements.md`.
> Solo describe lo que cambia; lo demás sigue como en `specs/design.md` y los paquetes anteriores.

**Estado:** Borrador v1 (2026-10-09) — pendiente de aprobación

---

## 1. Qué se toca

| Bloque | Backend | Frontend |
|---|---|---|
| **Formulario** (RF-40) | Migración de datos: orden de `QuoteFormField` | `QuoteCalculator.jsx` y `.css` |
| **Servicios** (RF-35 a RF-37, RF-41) | `Service.image`, `Service.image_alt`, nombre de la sección, `/api/site/` | `Services.jsx` y `.css`, `ServiceCard.jsx` (nuevo), `overlay.css` (nuevo) |
| **Proyectos** (RF-34, RF-38, RF-39, RF-41) | Migración de datos: texto del botón; panel sin "portada de su categoría" | `ProjectsTeaser.jsx` (reemplaza a `ProjectCategories`), `ProjectCard`, `ProjectDetailPage`, `Button` |

No hay modelos nuevos ni dependencias nuevas.

---

## 2. Backend

### 2.1 Modelos (`site_content/models.py`)

```python
class Service(OrderedModel, VisibleModel):
    ...
    image = site_image_field("imagen", blank=True)      # mismo ayudante que Portada y Proceso
    image_alt = models.CharField("texto alternativo de la imagen", max_length=150, blank=True)
```

- La imagen se valida con `validate_image_file` y se guarda optimizada y con nombre nuevo, igual que las demás imágenes de `site_content`.
- `ServicesSection`: `verbose_name` y `__str__` pasan de "Servicios (encabezado)" a **"Servicios"**.

### 2.2 Migraciones

| Migración | Qué hace |
|---|---|
| `site_content.0013_service_image` | Agrega `image` e `image_alt` a `Service`; cambia el nombre visible de `ServicesSection` |
| `site_content.0014_specs_004_texts` (datos) | `ProjectsSection.view_all_text`: "Ver todos los proyectos" → "Ver proyectos", **solo si sigue con el texto original**. `QuoteFormField`: `has_photos` pasa a ir antes de `message` |

Como no hay modelos nuevos, no hace falta migración de permisos en `core`.

### 2.3 API (`GET /api/site/`)

Cada elemento de `services.items` agrega:

```json
{ "id": 1, "title": "Levantamiento de espacio", "description": "...",
  "image": "http://.../media/site/2026/abc.jpg", "image_alt": "Medición de una sala" }
```

`image` es `null` si el servicio no tiene imagen. Lo demás no cambia. `/api/project-categories/` se conserva: lo usa el filtro de `/proyectos`.

### 2.4 Panel

- `ServiceInline`: campos `title`, `description`, `image`, `image_alt`, `is_visible`.
- `ProjectAdmin`: se quita `is_category_cover` del formulario. El campo sigue en el modelo.

### 2.5 Tests del backend

- API: `image` e `image_alt` en cada servicio; `null` sin imagen; dirección completa con imagen.
- Panel: el servicio acepta una imagen dentro de "Servicios"; un archivo falso se rechaza; el menú dice "Servicios".
- Migración 0014: el texto original se cambia y el del cliente se respeta; `has_photos` queda antes de `message`.
- Roles: un Viewer no puede cambiar la imagen de un servicio.

---

## 3. Frontend

### 3.1 Estructura (solo lo que cambia)

```
frontend/src/
├── styles/overlay.css                  nuevo: la capa con texto que comparten las tarjetas
├── components/
│   ├── home/ProjectsTeaser.jsx (.css)  nuevo: título y botón (reemplaza a ProjectCategories)
│   ├── home/ProjectCategories.*        se borra
│   ├── home/Services.jsx (.css)        fondo oscuro y cuadrícula de tarjetas
│   ├── home/ServiceCard.jsx            nuevo: portada, número, título y capa
│   ├── projects/CategoryCard.jsx       se borra
│   ├── projects/ProjectCard.*          usa la capa compartida; entrada suave en táctil
│   ├── quote/QuoteCalculator.*         orden y ancho de campos
│   └── ui/Button.*                     tamaño "large"
└── pages/ProjectDetailPage.*           capa sobre la portada
```

### 3.2 La capa compartida (`styles/overlay.css`) — RF-37, RF-38, RF-41

Una sola clase para las tres capas (tarjeta de proyecto, tarjeta de servicio y portada del detalle):

```css
.cover-overlay {            /* la capa oscura */
  position: absolute; inset: 0;
  opacity: 0; pointer-events: none;
  transition: opacity var(--motion-overlay) var(--ease-out);
}
.cover-overlay__content {   /* el texto (y el botón): sube mientras aparece */
  transform: translateY(12px);
  transition: transform var(--motion-overlay) var(--ease-out);
}
.cover-overlay__text {      /* la parte que se desplaza */
  overflow-y: auto;
  scrollbar-width: thin;                                   /* Firefox y Chrome nuevos */
  scrollbar-color: var(--color-on-dark-muted) transparent;
  mask-image: linear-gradient(to bottom, #000 calc(100% - 32px), transparent);
  padding-bottom: 32px;     /* la última línea queda por encima del degradado */
}
.cover-overlay__text::-webkit-scrollbar { width: 4px; }    /* Safari */
```

**Cuándo se ve la capa:**

| Dispositivo | Regla |
|---|---|
| Con cursor (`@media (hover: hover)`) | Al pasar el cursor por la tarjeta o al tener el foco dentro (`:hover`, `:focus-within`) |
| Táctil (`@media (hover: none)`) | Solo en las tarjetas de servicio: cuando `Reveal` les pone `.is-visible`, con un retraso corto para que entre después de la foto |
| "Reducir movimiento" | Mismas reglas, sin transición ni desplazamiento |

Token nuevo en `tokens.css`: `--motion-overlay: 450ms` (hoy la capa usa `--motion-hover`, más corto, y por eso se siente brusca).

### 3.3 Servicios (RF-35 a RF-37)

- `Services.jsx`: `<Section variant="dark">`, encabezado como hoy y la cuadrícula `.project-grid` que ya usan las tarjetas de proyecto.
- `ServiceCard.jsx`:
  ```jsx
  <Reveal as="article" index={index} className="service-card">
    <div className="service-card__media">
      {service.image ? <img src={service.image} alt={service.image_alt} loading="lazy" /> : null}
      <span className="service-card__number" aria-hidden="true">01</span>
      <div className="cover-overlay">
        <div className="cover-overlay__content">
          <p className="cover-overlay__text">{service.description}</p>
          {showCta && <Button to="/#contacto" size="small" onDark>Cotizar</Button>}
        </div>
      </div>
    </div>
    <h3 className="service-card__title">{service.title}</h3>
  </Reveal>
  ```
- La tarjeta no es un enlace: el único elemento que se pulsa es "Cotizar". Como recibe el foco, `:focus-within` muestra la capa a quien usa teclado.
- Aquí la descripción **no** va oculta a lectores de pantalla: es el único lugar donde se lee.
- Las entradas de izquierda/derecha de las tarjetas de texto se quitan: todas entran desde abajo, como las de proyecto.

### 3.4 Proyectos del inicio (RF-34)

- `ProjectsTeaser.jsx`: `<Section id="proyectos" variant="dark">` con el `h2` y el botón. Ya no pide categorías a la API.
- `Button` gana `size="large"`: más alto, `min-width: 320px` (100 % en celular) y una flecha `→` que se desplaza 6px al pasar el cursor (`transform`).
- Se borran `ProjectCategories.*` y `CategoryCard.jsx`. `getProjectCategories` se conserva para `/proyectos`.

### 3.5 Tarjetas de proyecto y detalle (RF-38, RF-39, RF-41)

- `ProjectCard`: su capa usa `.cover-overlay`. En táctil sigue sin capa; el bloque de texto de debajo (categoría, título y resumen) entra con un fundido y un pequeño desplazamiento, un instante después de la foto.
- `ProjectDetailPage`: dentro de `.project-detail__cover` se agrega la capa con `project.description`, oculta a lectores de pantalla (`aria-hidden`) porque la descripción ya está debajo. Solo existe con cursor. El contenedor conserva `overflow: clip` para no romper el zoom ligado al scroll.

### 3.6 Formulario (RF-40)

- Se quita la regla que hacía que "Ubicación" ocupara dos columnas.
- En `QuoteCalculator.jsx`, la casilla `has_photos` se mueve antes del campo `message`.

### 3.7 Tests del frontend

No hay lógica nueva que probar con Vitest (son cambios de presentación). Se verifica con `npm run lint`, `npm run build` y Playwright: tamaños de los campos, capa con cursor y con teclado, emulación táctil (`hasTouch`) para las entradas, y "reducir movimiento".

---

## 4. Registro de decisiones

| Decisión | Motivo |
|---|---|
| Una sola clase `.cover-overlay` para las tres capas | El scroll, el degradado y la animación se definen una vez y se ven igual en todo el sitio |
| `:focus-within` además de `:hover` | Quien navega con teclado también llega a "Cotizar" |
| En táctil la capa depende de `.is-visible` de `Reveal` | Reutiliza el `IntersectionObserver` que ya existe; sin JavaScript nuevo |
| Barra fina con `scrollbar-width` y `::-webkit-scrollbar` | Es CSS estándar; no hace falta una librería de scroll |
| `is_category_cover` se conserva en el modelo | Si el cliente vuelve a pedir las tarjetas de categorías, sus portadas siguen elegidas |

---

## 5. Riesgos

- **Servicios sin foto:** hasta que el cliente cargue las imágenes, la sección se ve con fondos lisos.
- **Fotos claras:** la capa oscura debe dar contraste suficiente al texto sobre cualquier imagen; se revisa con fotos reales.
- **Emulación táctil:** Playwright emula `hover: none`, pero la confirmación final es en un celular real.
