# Diseño — specs-011

> **Cómo** se construyen los requisitos de `specs/specs-011/requirements.md`.

**Estado:** Aprobado (2026-10-16), en implementación

---

## 1. Qué se toca

| Bloque | Requisitos | Archivos |
|---|---|---|
| **1. Backend** | RF-68 | `site_content/models.py` (nombres y ayudas), migración `0022_process_video_background.py`, `site_content/serializers.py`, tests |
| **2. Frontend** | RF-68, RF-69 | `utils/projectsBackground.js` → `utils/sectionBackground.js`, `components/ui/SectionBackground.jsx` (nuevo), `components/home/ProjectsTeaser.jsx`, `components/home/Process.jsx`, `Process.css`, tests |

Sin dependencias nuevas. Se reutiliza lo que hizo specs-009 para el fondo de Proyectos.

---

## 2. Backend

### 2.1 Modelo (`ProcessSection`)

Los campos ya existen (`video`, `video_poster`, `show_video`). Solo cambian sus textos en el panel:

| Campo | Nombre nuevo | Ayuda nueva |
|---|---|---|
| `video` | "video de fondo" | "Cubre toda la sección, detrás del título y las tarjetas. Se reproduce solo, en bucle y sin sonido. Súbelo corto y ya comprimido." |
| `video_poster` | "vista previa del video" | "Imagen que se ve mientras carga el video, y en lugar del video para quien pidió menos movimiento en su equipo." |
| `show_video` | "mostrar el video" (igual) | "Desmárcala para volver al fondo claro sin borrar el video." |

- Migración `site_content.0022_process_video_background`: solo `AlterField` de `verbose_name` y `help_text`. No toca columnas ni datos.

### 2.2 API (`ProcessSectionSerializer`)

Igual que `ProjectsSectionSerializer` en specs-009: con `show_video = False` devuelve **`null`** en `video` y `video_poster`, para que el navegador no conozca las direcciones ni descargue nada. Los campos de la respuesta no cambian de nombre.

### 2.3 Tests

- Con la casilla desmarcada, la API devuelve `null` en `video` y `video_poster` aunque estén cargados.
- Con la casilla marcada, devuelve las dos direcciones.

---

## 3. Frontend

### 3.1 Lógica compartida del fondo

`utils/projectsBackground.js` pasa a `utils/sectionBackground.js`, con una función general:

```js
// Devuelve null, { type: 'video', src, poster } o { type: 'image', src, alt }
export function pickSectionBackground({ video, image, alt }, reduceMotion)
```

- Misma regla de specs-009: el video gana; con "reducir movimiento" se usa la imagen; sin nada, `null`.
- `pickProjectsBackground(section, reduceMotion)` se queda como una línea que llama a la general, para que `ProjectsTeaser` y sus tests no cambien de comportamiento.
- `pickProcessBackground(process, reduceMotion)`: llama a la general con `video`, `video_poster` y `alt: ''` (la imagen es decoración).

### 3.2 Componente `SectionBackground`

El componente interno `ProjectsBackground` de `ProjectsTeaser.jsx` sale a `components/ui/SectionBackground.jsx` y lo usan las dos secciones. El video lleva:

```jsx
<video muted autoPlay loop playsInline preload="metadata" poster={...} aria-hidden="true" />
```

- **Sin `controls`**: así el navegador no dibuja botones (RF-69.3).
- `muted` + `playsInline`: es lo que piden Safari y Chrome en el celular para reproducir solo y sin abrir pantalla completa.
- `disablePictureInPicture` y `disableRemotePlayback`: evitan los botones flotantes que algunos navegadores agregan sobre los videos.
- `pointer-events: none` en `.section__background` (`Section.css`): tocar el video en el celular no hace nada ni muestra controles.

### 3.3 `Process.jsx`

- Calcula `background = pickProcessBackground(process, prefersReducedMotion())`.
- Pasa a `<Section>` la propiedad `background={background && <SectionBackground background={background} />}` (ya existe desde specs-009) y la clase `process--with-background`.
- Se quita el bloque `.process__media` con el `<video controls>`.
- Sin fondo, el HTML queda como hoy (RF-68.5).

### 3.4 CSS (`Process.css`)

Solo dentro de `.process--with-background`:

- Título e introducción en `var(--color-on-dark)`; la introducción con algo de transparencia, como los textos secundarios sobre oscuro.
- Tarjetas: fondo `color-mix(in srgb, var(--color-dark) 55%, transparent)`, contorno claro y semitransparente, título y número en blanco y descripción en `var(--color-on-dark-secondary)`. El número no va en `var(--color-accent)` porque ese token es casi negro (`#111`) y no se vería (P-71). Se comprueba el contraste en el navegador y, si hace falta, se sube la opacidad.
- La capa oscura general es la de `Section.css` (`.section--with-background::after`); no se escribe otra.
- `.section__background` ya tiene `object-fit: cover` e `inset: 0`, así que el video cubre toda la sección, tarjetas incluidas (RF-68.1 y RF-68.4).
- Se borran las reglas de `.process__media` y `.process__video`.

### 3.5 Tests (Vitest)

- Se renombra `projectsBackground.test.js` a `sectionBackground.test.js`; los casos de Proyectos se mantienen.
- Casos nuevos de `pickProcessBackground`: sin video → `null`; video y vista previa → video con `poster`; con "reducir movimiento" → la vista previa como imagen, o `null` si no hay.

Lo visual (que no hay controles, que el video llena la sección y que arranca solo en el celular) se comprueba en el navegador con Playwright.

---

## 4. Registro de decisiones

| Decisión | Motivo |
|---|---|
| Se reutilizan los campos actuales del video de Proceso | El cliente ya tiene el video cargado; no hay que volver a subirlo |
| Se generaliza la lógica del fondo de specs-009 en vez de copiarla | Una sola regla para los dos fondos, probada en un solo lugar |
| El serializer oculta los archivos con la casilla desmarcada | Igual que Proyectos: ahorra la descarga |

## 5. Riesgos

- **iPhone en modo de bajo consumo:** Safari puede no reproducir videos solos. En ese caso se ve la vista previa fija, sin botón de reproducir encima (el video no tiene `controls`). Conviene que el cliente cargue una vista previa.
- **Videos en iPhone desde Railway:** misma limitación de la demo (specs-006 §6) mientras los archivos sigan en el volumen de Railway.
- **Peso:** el video se descarga en todos los celulares que abren el inicio. Si pesa mucho, baja la nota de Lighthouse (RF-06). La ayuda del panel pide subirlo corto y comprimido.
