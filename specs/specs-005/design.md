# Diseño — specs-005

> **Cómo** se construyen los requisitos de `specs/specs-005/requirements.md`.
> Solo describe lo que cambia; lo demás sigue como en `specs/design.md` y los paquetes anteriores.

**Estado:** Implementado y cerrado (2026-10-13)

---

## 1. Qué se toca

| Bloque | Backend | Frontend |
|---|---|---|
| **1. Formulario y cuadrícula** (RF-42 a RF-44) | `quotes/views.py`, `quotes/serializers.py`, ayuda de `ProjectCategory.is_visible` | `quoteValidation.js`, `Services.jsx` y `.css` |
| **2. Capas en celular y detalle** (RF-45, RF-46) | — | `hooks/useInCenter.js` (nuevo), `overlay.css`, `ServiceCard`, `ProjectCard`, `ProjectDetailPage` |
| **3. Animaciones y encabezado** (RF-47, RF-48) | — | `useReveal.js`, `motion.css`, `useHideOnScroll.js` / `Header.jsx` |

Sin modelos nuevos ni dependencias nuevas.

---

## 2. Backend (bloque 1)

### 2.1 Categorías en el formulario (RF-42)

- `QuoteCategoryListView`: recorre `ProjectCategory.objects.all()` (antes, solo las visibles).
- `QuoteCreateSerializer.category`: `queryset=ProjectCategory.objects.all()`.
- `ProjectListView` y `ProjectCategoryListView` **no cambian**: siguen usando solo las visibles.
- `ProjectCategory.is_visible`: nuevo texto de ayuda — "Si se desmarca, la categoría sale del filtro de proyectos. Sus proyectos siguen viéndose en "Todos" y el formulario la sigue ofreciendo." Genera la migración `projects.0006` (solo cambia el texto).

### 2.2 Ubicación obligatoria (RF-43)

- `QuoteCreateSerializer`: `location` con `required=True`, `allow_blank=False` y el mensaje "Escribe la ubicación del espacio."
- El modelo `Quote.location` **sigue con `blank=True`**: las cotizaciones anteriores no tienen ubicación y deben poder abrirse en el panel. No hay migración.

### 2.3 Tests del backend

- `/api/quote-categories/` incluye una categoría oculta; `POST /api/quotes/` la acepta.
- `/api/project-categories/` y `?category=<oculta>` siguen como en specs-003.
- `POST /api/quotes/` sin `location`, o con solo espacios, responde `400` en `location`.

---

## 3. Frontend

### 3.1 Bloque 1

- `quoteValidation.js`: `location` vacío → "Escribe la ubicación del espacio." Con su test.
- `Services`: cuadrícula propia `.services__grid` en lugar de `.project-grid`:
  ```css
  .services__grid { display: grid; grid-template-columns: 1fr; gap: var(--space-24); }
  @media (min-width: 600px)  { .services__grid { grid-template-columns: repeat(2, 1fr); } }
  @media (min-width: 1100px) { .services__grid { grid-template-columns: repeat(var(--service-columns), 1fr); } }
  ```
  `--service-columns` lo pone el componente: `Math.min(servicios, 4)`. Con 3 servicios hay 3 columnas; con 4 o más, 4.

### 3.2 Bloque 2 — capa al centrarse (RF-46)

- Hook nuevo `useInCenter()`: un `IntersectionObserver` con `rootMargin: '-50% 0px -50% 0px'`, que deja como zona de observación solo la **línea central** de la pantalla (ajustado al implementar: con una franja del 30 % podían coincidir dos tarjetas). Devuelve `{ ref, isInCenter }` y, a diferencia de `useReveal`, **no deja de observar**: el valor cambia cada vez que la tarjeta entra o sale de la franja.
- Solo se activa en táctil (`matchMedia('(hover: none)')`); con cursor devuelve siempre `false` y no crea el observador.
- La portada recibe la clase `is-centered`. En `overlay.css`, dentro de `@media (hover: none)`:
  ```css
  .has-cover-overlay.is-centered .cover-overlay { opacity: 1; pointer-events: auto; }
  .has-cover-overlay.is-centered .cover-overlay__content { transform: none; }
  ```
- Se quita la variante `cover-overlay--auto` (capa fija al aparecer) y la entrada retrasada de `.project-card__text`.
- En las tarjetas de proyecto, la capa en táctil no atrapa el dedo (`pointer-events: none`), porque la tarjeta entera es un enlace; **el texto sí** (`pointer-events: auto`), para poder desplazar una descripción larga. Corregido tras la prueba del desarrollador: con toda la capa desactivada se veía la barra pero el texto no bajaba.
- "Reducir movimiento" en táctil: `useInCenter` devuelve `true` fijo en servicios y detalle (parámetro `alwaysWhenReduced`).

### 3.3 Bloque 2 — detalle (RF-45)

- Se borra el párrafo `.project-detail__description`.
- La capa de la portada pierde `aria-hidden`; el texto recibe `tabIndex={0}` para poder enfocarlo y desplazarlo con el teclado (`:focus-within` ya muestra la capa).

### 3.4 Bloque 3 — entradas (RF-47)

**Medición (Android emulado, 390 × 800):** cada entrada empezaba con el borde superior del elemento entre el **87 % y el 99 %** del alto de la pantalla, es decir, cuando apenas asomaba por abajo. Con la curva `--ease-out`, que hace casi todo el cambio en los primeros 150 ms, la animación terminaba antes de que el elemento estuviera a la vista. Esa es la causa de que "no se vean" o se sientan toscas.

**Corrección:**
- `useReveal`: `rootMargin: '0px 0px -12% 0px'` y `threshold: 0.1`. La entrada empieza cuando el elemento ya subió por la pantalla.
- Red de seguridad: al llegar al final de la página se muestra todo lo que falte. Sin ella, un elemento que quede en el 12 % inferior cuando la página ya no baja más nunca cruzaría la línea (RF-06: nada queda oculto).
- `motion.css` y `tokens.css`: `.reveal` usa `--ease-soft`; `--motion-reveal` pasa de 500 a 700 ms y `--reveal-distance` de 24 a 32 px.

Los cambios aplican también en escritorio: es el mismo componente.

### 3.5 Bloque 3 — encabezado (RF-48)

**Causa (reproducida con Playwright):** `Header.css` tenía `.header:focus-within { transform: none }`, pensado para que el encabezado no se esconda a quien navega con teclado. Pero al pulsar el logo con el mouse o el dedo, el foco se queda en el logo; el encabezado recibía la clase `is-hidden` al bajar y esa regla la anulaba, así que quedaba fijo hasta pulsar en otro lugar.

**Corrección:** `.header:has(:focus-visible)`. `:focus-visible` solo aplica al foco de teclado, que es para quien estaba pensada la regla.

---

## 4. Registro de decisiones

| Decisión | Motivo |
|---|---|
| `Quote.location` sigue opcional en el modelo | Las cotizaciones anteriores no la tienen; la obligación va en el serializer, que es lo que usa el sitio |
| `useInCenter` separado de `useReveal` | Uno se dispara una vez; el otro cambia en cada pasada. Mezclarlos complicaría los dos |
| Línea central en lugar de una franja | Nunca hay dos tarjetas activas a la vez |
| Medir antes de ajustar las animaciones | El síntoma viene del teléfono del desarrollador; hay que confirmar la causa |

---

## 5. Riesgos

- **Emulación ≠ teléfono real:** las animaciones se confirman al final en el Android del desarrollador.
- **Ajustes del teléfono:** con "quitar animaciones" o ahorro de batería, el sitio no anima a propósito.
- **Tarjetas angostas:** con 4 columnas hay menos sitio para la descripción; se resuelve con el scroll de la capa.
