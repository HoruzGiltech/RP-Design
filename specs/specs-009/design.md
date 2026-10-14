# Diseño — specs-009

> **Cómo** se construyen los requisitos de `specs/specs-009/requirements.md`.

**Estado:** Implementado y cerrado (2026-10-14)

---

## 1. Qué se toca

| Bloque | Requisitos | Archivos |
|---|---|---|
| **1. Backend** | RF-65, RF-66 | `site_content/models.py`, migración `0021_projects_section_background.py`, `site_content/serializers.py`, tests |
| **2. Frontend** | RF-65, RF-66 | `components/home/ProjectsTeaser.jsx`, `ProjectsTeaser.css`, tests |

Sin dependencias nuevas.

---

## 2. Backend

### 2.1 Modelo (`ProjectsSection`)

Se reutilizan `site_image_field` y `site_video_field`, que ya traen las validaciones de formato, tamaño y tipo real (RF-02, specs-007):

```python
background_image = site_image_field(
    "imagen de fondo",
    help_text="Ocupa todo el ancho de la sección, con el título encima. "
              "También es la vista previa del video.",
)
background_image_alt = models.CharField("texto alternativo de la imagen", max_length=150, blank=True)
background_video = site_video_field(
    "video de fondo",
    help_text="Opcional. Se reproduce en bucle y sin sonido en lugar de la imagen. "
              "Súbelo corto y ya comprimido.",
)
show_background = models.BooleanField(
    "mostrar la imagen o el video de fondo",
    default=False,
    help_text="Desmárcala para volver al fondo negro sin borrar los archivos.",
)
```

- `save()` llama a `optimize_image_field(self, "background_image")`, como `HeroSection` y `ProcessSection`.
- El panel sigue con `SectionAdmin`: muestra los campos nuevos solo y ya trae la revisión de archivos de specs-007 (`FileCheckMixin`).
- Migración `site_content.0021_projects_section_background`: solo agrega columnas, no toca datos.

### 2.2 API (`ProjectsSectionSerializer`)

Agrega `show_background`, `background_image`, `background_image_alt` y `background_video`.

Con `show_background = False` devuelve **`null`** en `background_image` y `background_video`. Así el navegador no conoce las direcciones y no descarga nada (CA-66.1).

### 2.3 Tests

- Con la casilla desmarcada, la API devuelve `null` en los dos archivos aunque estén cargados.
- Con la casilla marcada, devuelve las dos direcciones.
- Prueba de humo: se rechaza un video con otro formato (el validador común ya está probado).

---

## 3. Frontend (`ProjectsTeaser`)

- **`utils/projectsBackground.js`**: función pura `pickProjectsBackground(section, reduceMotion)`. Devuelve `null` (sin fondo), `{ type: "video", src, poster }` o `{ type: "image", src, alt }`. Toda la regla de RF-65 y RF-66 vive aquí, para poder probarla sin navegador.
- **`ProjectsBackground`** (componente interno de `ProjectsTeaser.jsx`) dibuja lo que devuelve la función:
  - Video: `<video autoPlay muted loop playsInline poster preload="metadata" aria-hidden="true">`. La comprobación de "reducir movimiento" es `prefersReducedMotion()` de `hooks/useReveal.js`.
  - Imagen: `<img decoding="async" alt>`, con alt vacío si no hay texto.
- **`Section`** gana una propiedad opcional `background`: lo dibuja detrás del contenido, pegado a los bordes de la `<section>` (no al contenedor del texto), y le agrega la clase `section--with-background`. Sin esa propiedad, el HTML y el CSS quedan como hoy (CA-65.3).

### 3.1 CSS

- `Section.css`: `.section--with-background` con `position: relative` e `isolation: isolate`; su `.section__inner` va encima (`position: relative`).
- `.section__background`: `position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: -2`.
- Capa oscura con `::after` (`z-index: -1`): un degradado negro semitransparente con los tokens de color, como la capa del hero, para que el texto blanco se lea sobre cualquier foto.
- `ProjectsTeaser.css`: con fondo, el contenido mide `min-height: 60vh` (`50vh` en el celular) y va centrado en vertical.
- `object-fit: cover` evita que la imagen se deforme en el celular (CA-65.4).

### 3.2 Tests (Vitest)

El proyecto no tiene librería para probar componentes de React, y no se agrega una solo para esto. Se prueba `pickProjectsBackground`:

- Casilla desmarcada o sin archivos: `null`.
- Solo imagen: imagen con su `alt`.
- Imagen y video: video, con la imagen como `poster`.
- Solo video: video sin `poster`.
- Con "reducir movimiento": la imagen si hay; `null` si solo hay video.

Lo visual (capa, alto, celular) se comprueba en el navegador con Playwright (S9-C4).

---

## 4. Registro de decisiones

| Decisión | Motivo |
|---|---|
| Campos en `ProjectsSection` y no en un modelo aparte | Es un solo fondo por sección, igual que el video de Proceso |
| El serializer oculta los archivos con la casilla desmarcada | Ahorra la descarga y el frontend no tiene que mirar la casilla |
| `<img>` y `<video>` reales en vez de `background-image` en CSS | Permiten `alt`, carga diferida y `poster`, como el resto del sitio |

## 5. Riesgos

- **Videos en iPhone:** misma limitación de la demo (specs-006 §6) mientras los archivos sigan en el volumen de Railway.
- **Peso:** un video pesado hace lenta la página en el celular. La ayuda del panel pide subirlo corto y comprimido, y se usa `preload="metadata"`.
