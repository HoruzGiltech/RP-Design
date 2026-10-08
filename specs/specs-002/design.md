# Diseño técnico — specs-002

> **Cómo** se construye lo que pide `specs/specs-002/requirements.md`.
> Solo describe lo que cambia. Lo que no aparece aquí sigue como en `specs/design.md` y `specs/specs-001/design.md`.

**Estado:** Aprobado (v1, 2026-10-07)

---

## 1. Qué se toca

```
backend/quotes/         áreas por categoría, tipo en la cotización, API y mensaje
backend/site_content/   interruptores de los botones del hero; aviso en Especialidades
backend/projects/       solo el panel de categorías (muestra cuántas áreas tiene)
frontend/src/           encabezado, hero, inicio, formulario y sección Contacto
```

No se agregan dependencias, ni en el backend ni en el frontend.

---

## 2. Backend

### 2.1 Modelos

**RemodelArea** (`quotes`) — cambios

| Campo | Cambio |
|---|---|
| `category` | FK nuevo → `projects.ProjectCategory`, `null=True`, `blank=True`, `on_delete=PROTECT`, `related_name="remodel_areas"`. Vacío significa "aparece en todas las categorías" (RF-17.4) |
| `slug` | Deja de escribirse a mano: se genera del nombre al crear, como en proyectos y categorías. Dos áreas pueden llamarse igual en categorías distintas ("Sala"); la segunda recibe `-2` |

**Quote** (`quotes`) — cambios

| Campo | Cambio |
|---|---|
| `category` | FK nuevo → `projects.ProjectCategory`, `null=True`, `on_delete=SET_NULL`. El tipo de remodelación elegido. Vacío en las cotizaciones anteriores |
| `category_name` | Char(60) nuevo. Copia del nombre del tipo en ese momento, para que la cotización lo conserve aunque la categoría cambie de nombre o se elimine |

**HeroSection** (`site_content`) — cambios

| Campo | Cambio |
|---|---|
| `show_primary_cta` | Bool nuevo, "Mostrar el botón principal", por defecto `True` |
| `show_secondary_cta` | Bool nuevo, "Mostrar el botón secundario", por defecto `True` |

**Specialty** (`site_content`): el modelo no cambia. Su nombre en el panel pasa a "especialidades (ya no se muestran en el sitio)".

> **Decisión:** las áreas se enlazan con `ProjectCategory`, el mismo modelo de las categorías de proyectos (P-11). El cliente mantiene una sola lista y el formulario habla el mismo idioma que el portafolio.

### 2.2 Migraciones

| App | Migración | Qué hace |
|---|---|---|
| `quotes` | `0004_area_category` | Agrega `RemodelArea.category`, `Quote.category` y `Quote.category_name`. `RemodelArea.slug` pasa a no editable |
| `quotes` | `0005_assign_area_categories` (datos) | Asigna a **Residencial** las áreas que no sean "Otro" y no tengan categoría. Crea Oficina y Sala de reuniones (Corporativo) y Showroom (Comercial), sin precio, si no existen. "Otro" queda sin categoría |
| `site_content` | `0010_hero_cta_switches` | Agrega los dos interruptores del hero. Cambia el nombre de "Especialidades" en el panel |

- La migración de datos depende de `projects.0003`, que es la que crea las categorías.
- Si una categoría inicial ya no existe (el cliente la borró), sus áreas de ejemplo no se crean.
- No hace falta migración de permisos: no hay modelos nuevos.

### 2.3 Reglas de negocio (`quotes/services.py`)

```python
def area_belongs_to_category(area, category) -> bool:
    """True si el área es de esa categoría o es común a todas (sin categoría)."""

def build_whatsapp_message(quote: Quote) -> str: ...   # agrega la línea del tipo
```

Mensaje de WhatsApp, con la línea nueva:

```
Hola RP Design, quiero una cotización:

👤 Nombre: {name}
📧 Correo: {email}
📱 Teléfono: {phone}
🏗️ Tipo: {category_name}        ← nueva. Se omite si la cotización no tiene tipo
🏠 Área: {area}
📐 Metros cuadrados: {m2} m²
💲 Estimado: {estimate}

💬 Mensaje: {message}
```

### 2.4 API

| Método | Ruta | Cambio |
|---|---|---|
| GET | `/api/quote-categories/` | **Nuevo.** Tipos de remodelación con sus áreas, en una sola llamada |
| GET | `/api/quote-areas/` | **Se elimina.** Lo reemplaza el anterior |
| POST | `/api/quotes/` | Nuevo campo obligatorio `category` (id). Valida que el área pertenezca a ese tipo |
| GET | `/api/site/` | `hero` agrega `show_primary_cta` y `show_secondary_cta`. `specialties` deja de enviarse |

Respuesta de `/api/quote-categories/`:

```json
[
  { "id": 2, "name": "Residencial", "slug": "residencial",
    "areas": [
      { "id": 1, "name": "Baño", "price_per_m2": "10.00", "is_other": false },
      { "id": 6, "name": "Otro", "price_per_m2": null,   "is_other": true }
    ] }
]
```

- Las categorías van en el orden del panel. Dentro de cada una, primero sus áreas en su orden y al final las comunes a todas ("Otro").
- Solo áreas activas. Una categoría sin ninguna área no se envía (RF-17.8).

`POST /api/quotes/`, validación nueva:

| Caso | Respuesta |
|---|---|
| Falta `category` o no existe | `400` en `category`: "Elige el tipo de remodelación." |
| El área no es de ese tipo ni es común | `400` en `area`: "Elige un área de la lista." |

El backend guarda `category` y `category_name` y arma el mensaje con el tipo. El honeypot y los límites de peticiones no cambian.

### 2.5 Panel

| Modelo | Cambios |
|---|---|
| RemodelArea | Columna y filtro por categoría; `category` editable desde la lista junto al precio. Sin campo de identificador. Ayuda en `category`: "Déjala vacía para que el área aparezca en todos los tipos (por ejemplo, Otro)" |
| ProjectCategory | Columna nueva "Áreas del formulario" con cuántas tiene. Si se intenta borrar una categoría con áreas, Django lo impide y lo explica |
| Quote | Muestra el tipo en la lista y en el detalle; filtro por tipo |
| HeroSection | Los dos interruptores, junto al texto de cada botón |
| Specialty | Sigue en el menú, con el nombre que avisa de que ya no se muestra |

### 2.6 Tests del backend

| Qué | Dónde |
|---|---|
| `area_belongs_to_category`: propia, ajena y común | `quotes/tests/test_services.py` |
| Mensaje con y sin tipo | `quotes/tests/test_services.py` |
| Migración: áreas actuales → Residencial; "Otro" sin categoría; se crean las tres nuevas | `quotes/tests/test_models_and_admin.py` |
| `/api/quote-categories/`: agrupa bien, "Otro" en todas, orden, oculta inactivas y categorías vacías | `quotes/tests/test_api.py` |
| `POST`: exige `category`; rechaza un área de otro tipo; acepta "Otro" con cualquier tipo; guarda `category` y `category_name` | `quotes/tests/test_api.py` |
| El slug del área se genera solo y no choca con nombres repetidos | `quotes/tests/test_models_and_admin.py` |
| `/api/site/`: interruptores del hero; sin `specialties` | `site_content/tests/test_api.py` |
| Categoría con áreas no se elimina | `projects/tests/test_admin.py` |

---

## 3. Frontend

### 3.1 Estructura (solo lo que cambia)

```
frontend/src/
├── api/endpoints.js                 + getQuoteCategories()   - getQuoteAreas()
├── hooks/useHideOnScroll.js         nuevo: dice si el encabezado debe ocultarse
├── components/
│   ├── layout/Header.jsx            menú siempre desplegable; se oculta al bajar
│   ├── home/Hero.jsx                respeta los interruptores de los botones
│   ├── home/HeroControls.jsx        controles discretos (RF-15)
│   ├── home/Contact.jsx             una sola columna
│   ├── home/ContactInfo.jsx         datos en fila
│   ├── home/SpecialtiesStrip.*      se borra
│   ├── ui/Marquee.*                 se borra (solo lo usaba el cintillo)
│   └── quote/QuoteCalculator.jsx    campo "Tipo de remodelación"; campos en columnas
├── pages/HomePage.jsx               sin <SpecialtiesStrip />
└── utils/quoteValidation.js         valida el tipo
```

### 3.2 Encabezado (RF-13)

Distribución, igual en todos los anchos:

```
┌──────────────────────────────────────────────────────────────┐
│ (RP) RP DISEÑO                          [Cotiza tu proyecto] │
│      INTERIOR · ARQUITECTURA                                 │
│  ☰                                                           │  ← el botón, debajo del logo
├──────────────────────────────────────────────────────────────┤
│ Servicios                                                    │  ← solo con el menú abierto
│ Proyectos                                                    │
│ Proceso                                                      │
└──────────────────────────────────────────────────────────────┘
```

- El botón ☰ va **debajo del logo**, con su mismo ancho, así las tres rayas quedan centradas bajo él. Conserva `aria-expanded`, `aria-controls` y el texto oculto "Abrir menú" / "Cerrar menú".
- Las opciones se despliegan en un panel debajo del encabezado, alineadas a la izquierda con el logo (RF-13.2).
- El encabezado gana una fila: `scroll-padding-top` sube de 96 a 136 px para que un ancla no quede tapada.
- "Cotiza tu proyecto": en escritorio sigue en la barra, a la derecha y a la altura del logo; por debajo de 768 px sigue dentro del panel, como hoy (RF-13.3).
- El panel se cierra al elegir una opción y con `Esc` (ya existe) y, nuevo, al pulsar fuera (`pointerdown` en el documento).

**Ocultar al bajar** (`useHideOnScroll`):

```js
// true cuando la persona está bajando y ya pasó el alto del encabezado
const isHidden = useHideOnScroll({ disabled: isMenuOpen })
```

- Escucha `scroll` (con `passive: true`) y compara la posición con la anterior: baja → ocultar; sube → mostrar. Ignora movimientos de menos de 8 px, para que no parpadee.
- Cerca del inicio de la página (menos que el alto del encabezado) siempre se muestra.
- No se oculta con el menú abierto ni con el foco dentro (`:focus-within` lo fuerza visible por CSS, CA-13.5).
- El encabezado sigue siendo `position: sticky`. Ocultarlo es `transform: translateY(-100%)` con `transition` de `--motion-hover`: no mueve el contenido (RNF-11).
- `scroll-padding-top` se mantiene, para que un ancla no quede bajo el encabezado cuando está visible.
- Con `prefers-reduced-motion`, sin transición.

### 3.3 Hero (RF-14 y RF-15)

**Botones:** `Hero` muestra cada botón solo si su interruptor está activado y su sección de destino está visible. Si no queda ninguno, no se dibuja el contenedor de los botones.

**Controles**, de esto:

```
RESIDENCIAL                                   [←] [❚❚] [→]
Nombre del proyecto →                          ▬ ▭ ▭
```

a esto:

```
RESIDENCIAL
Nombre del proyecto →                    ‹  ▰▱ ▭ ▭  ›   ❚❚
```

| Elemento | Detalle |
|---|---|
| Indicadores | Barras de 2 px de alto. La activa tiene dentro un relleno que crece de izquierda a derecha con `transform: scaleX(0 → 1)` durante `--slide-duration` |
| Progreso en pausa | El relleno solo lleva la animación mientras la rotación corre (`isRunning` de `useSlideshow`). Detenida, se muestra lleno y quieto. Al reanudar, la animación empieza de cero, igual que el temporizador de la portada: así nunca se desincronizan |
| Flechas | `‹` y `›`, sin borde ni fondo, `opacity: 0.6`; `1` con hover o foco |
| Pausa | `❚❚` / `▶` pequeño, sin borde, misma opacidad |
| Área pulsable | Cada botón mide 44 × 44 px aunque su dibujo sea de unos 12 px (CA-15.2) |
| Móvil | La línea de controles va debajo del nombre del proyecto, a la izquierda, dejando libre la esquina del botón flotante |

- Se conservan todos los nombres accesibles y el comportamiento de `useSlideshow`. Solo cambia el dibujo.
- Con `prefers-reduced-motion`, el relleno de la barra activa se muestra completo y quieto.

> **Decisión:** los controles no se quitan. La guía de `ui-ux-pro-max` para contenido que rota solo pide conservar anterior, siguiente y pausa, y la pauta de accesibilidad sobre movimiento exige poder detenerlo.

### 3.4 Inicio sin cintillo (RF-16)

- `HomePage` deja de montar `SpecialtiesStrip`. Se borran ese componente y `Marquee`, y los tokens `--marquee-duration` y `--col-strip`.
- Después del hero viene la sección Proyectos (orden de specs-001, P-8). Las dos son oscuras: se separan con una línea fina (`--color-dark-surface`) para que no parezcan un solo bloque.

### 3.5 Formulario (RF-17)

- `QuoteCalculator` pide `getQuoteCategories()` en lugar de `getQuoteAreas()`.
- Estado nuevo en el formulario: `category` (id como texto, igual que `area`).
- **Tipo de remodelación:** `<select>` con "Elige una opción" y una opción por categoría.
- **Área a remodelar:** `<select>` con las áreas de la categoría elegida. Sin tipo elegido, está `disabled` y su primera opción dice "Elige primero el tipo".
- Al cambiar el tipo: `area` y `area_other` vuelven a vacío (RF-17.6).
- El estimado, el control de metros y "Especifica el área" funcionan igual que hoy.
- Se envía `category` (número) junto con lo demás.
- `validateQuote` agrega: `category` obligatorio ("Elige el tipo de remodelación.").

### 3.6 Sección Contacto (RF-18)

```
Cuéntanos sobre tu espacio
Te respondemos con los próximos pasos…

┌───────────────────────────────────────────────────────────────┐
│ Nombre              │ Teléfono            │ Correo             │
│ Tipo de remodelación│ Área a remodelar    │ Especifica el área │
│ Metros cuadrados  ───────●──────  120 m²  │ Estimado           │
│                                           │ USD 1.200,00       │
│ Mensaje (opcional)                                             │
│ ☐ Acepto la política de privacidad…                            │
│ [            Enviar por WhatsApp             ]                 │
└───────────────────────────────────────────────────────────────┘

WhatsApp: +58 412 730 5964   ·   correo   ·   Instagram @…   ·   Caracas, Venezuela
```

- `Contact`: deja la grilla de dos columnas; pasa a `flex-direction: column` con título, introducción, formulario y datos de contacto.
- `QuoteCalculator`: el formulario pasa a `display: grid` de 3 columnas desde 900 px, 2 columnas desde 600 px y 1 columna por debajo. Los campos se colocan por orden; "Mensaje", la aceptación y el botón ocupan toda la fila (`grid-column: 1 / -1`); el control de metros ocupa 2 columnas.
- "Especifica el área" solo existe con "Otro": cuando no está, su celda queda vacía y la fila conserva su forma.
- El orden del HTML es el orden visual, así `Tab` recorre los campos en orden (CA-18.3).
- `ContactInfo`: `flex-direction: row` con `flex-wrap`, separación `--space-32`. En móvil cada dato baja de línea si no cabe.
- La pantalla de éxito y los estados de carga y error del formulario ocupan el mismo ancho completo.

### 3.7 Tests del frontend

| Qué | Cómo |
|---|---|
| `validateQuote`: exige el tipo | Vitest |
| Encabezado: menú cerrado por defecto a 1280 y 360 px; abre, cierra con `Esc`, al elegir y al pulsar fuera | Playwright |
| Encabezado: se oculta al bajar, vuelve al subir, no se oculta con el menú abierto, aparece con `Tab` | Playwright |
| Hero: combinaciones de botones; controles nuevos con mouse y teclado; áreas pulsables de 44 px | Playwright |
| Inicio sin cintillo | Playwright |
| Formulario: áreas según el tipo, reinicio del área al cambiar de tipo, envío real y mensaje con el tipo | Playwright |
| Contacto a 360, 768, 1280 y 1920 px, sin scroll horizontal; orden de `Tab` | Playwright |

---

## 4. Registro de decisiones

| # | Decisión | Motivo |
|---|---|---|
| D-37 | Las áreas se enlazan con las categorías de proyectos | Una sola lista que mantener; el formulario y el portafolio usan los mismos nombres |
| D-38 | Un área sin categoría es común a todas | Resuelve "Otro" sin repetirlo en cada categoría |
| D-39 | La cotización guarda el tipo y una copia de su nombre | El historial no depende de que la categoría siga existiendo |
| D-40 | `/api/quote-categories/` reemplaza a `/api/quote-areas/` | El formulario necesita tipos y áreas juntos; una llamada en vez de dos |
| D-41 | El encabezado se oculta con `transform`, sin dejar de ser `sticky` | No mueve el contenido ni recalcula la página al hacer scroll |
| D-42 | Los controles del hero se atenúan, no se eliminan | Lo pide la guía de `ui-ux-pro-max` y la accesibilidad: contenido que rota solo debe poder pararse |
| D-43 | "Especialidades" se conserva en el panel | Decisión del desarrollador: se quita del sitio, no se borra |
| D-44 | El identificador de las áreas se genera solo | Permite nombres repetidos en categorías distintas sin que el cliente piense en identificadores |

## 5. Riesgos

| Riesgo | Cómo se atiende |
|---|---|
| El menú desplegable en escritorio esconde la navegación | Es un pedido explícito del cliente. "Cotiza tu proyecto" sigue a la vista y el botón flotante de WhatsApp también |
| El encabezado que se oculta desorienta al navegar por anclas | Reaparece al subir y con el foco del teclado; arriba del todo está siempre |
| El cliente deja una categoría sin áreas | Esa categoría no aparece en el formulario (RF-17.8); el panel muestra cuántas áreas tiene cada una |
| Controles del hero demasiado discretos sobre fotos claras | Van sobre la capa oscura del hero; se revisa el contraste con fotos de prueba claras |
| Se rompe el formulario para quien tenga la página abierta durante el cambio de API | Solo afecta en producción y aún no hay despliegue |
