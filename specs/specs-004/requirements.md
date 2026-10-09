# Requisitos — specs-004: cuarta ronda de cambios del cliente

> **Qué** cambia respecto a lo ya construido y **cómo sabemos que está bien hecho**.
> Es un paquete de cambios sobre `specs/` y los paquetes `specs-001` a `specs-003`. Donde este documento los contradice, **manda este**.

**Estado:** Borrador v1 (2026-10-09) — pendiente de aprobación
**Base:** `specs/` (RF-01 a RF-07), `specs-001` (RF-08 a RF-12), `specs-002` (RF-13 a RF-18) y `specs-003` (RF-19 a RF-33), ya implementadas y cerradas.
**Reglas:** las mismas de `AGENTS.md`: mismo stack, mismos tokens de diseño, SDD, tests, accesibilidad y animaciones solo con CSS.

> ⚠️ **El despliegue sigue pendiente y sin empezar.** Es la última fase del proyecto (`specs/tasks.md`, Fase 5) y viene después de este paquete. Ver §6.

---

## 1. Resumen de los cambios

| # | Pedido del cliente | Requisito |
|---|---|---|
| 1 | En la sección Proyectos del inicio queda solo el botón, más llamativo y más ancho | RF-34 |
| 2 | Servicios se ve como se veía Proyectos: tarjetas con portada | RF-35 |
| 3 | En el panel, "Servicios (encabezado)" pasa a "Servicios" y cada servicio lleva su imagen | RF-36 |
| 4 | Al pasar el mouse por un servicio salen la descripción breve y el botón "Cotizar" | RF-37 |
| 5 | Scroll elegante en la descripción completa de las tarjetas de proyecto | RF-38 |
| 6 | En el detalle del proyecto, la descripción sale sobre la portada | RF-39 |
| 7 | La animación de "Cotizar" es brusca: hacerla más suave | RF-37 |
| 8 | "Ubicación del espacio" del mismo tamaño que "Tipo de remodelación" | RF-40 |
| 9 | La casilla "Tengo fotos del espacio" va arriba del mensaje | RF-40 |
| 10 | En móvil, lo que depende de pasar el mouse entra con animaciones suaves | RF-41 |

**Se prueba por partes.** El paquete se implementa en tres bloques, cada uno con su pausa para que el desarrollador lo pruebe: Formulario, Servicios y Proyectos (ver `tasks.md`).

---

## 2. Requisitos funcionales

### RF-34 — Sección Proyectos del inicio: título y botón

1. La sección Proyectos del inicio deja de mostrar las tarjetas de categorías. Quedan el **título** de la sección y **un botón** que lleva a `/proyectos`.
2. El botón es más llamativo que los demás del sitio: más alto, más ancho (ocupa todo el ancho en celular) y con una flecha que se desplaza al pasar el cursor.
3. El texto del botón sale del panel (campo que ya existe). Pasa a decir **"Ver proyectos"**; si el cliente ya lo había cambiado, se respeta su texto.
4. El enlace a Instagram de esa sección se quita: Instagram ya está en el pie (RF-33).
5. Las categorías **no desaparecen**: siguen siendo el filtro de `/proyectos` (RF-09).

**Criterios de aceptación**
- [ ] CA-34.1 En el inicio no hay tarjetas de categorías; el botón lleva a `/proyectos`.
- [ ] CA-34.2 El botón se usa con teclado y se ve su foco.
- [ ] CA-34.3 `/proyectos` sigue filtrando por categoría.

### RF-35 — Servicios con portada

1. La sección Servicios toma el aspecto que tenía la sección Proyectos: fondo oscuro y una cuadrícula de tarjetas con foto.
2. Cada tarjeta es un servicio: su **portada**, su número (01, 02…) y su **título**.
3. Un servicio sin imagen se muestra con un fondo oscuro liso en lugar de la foto; no rompe la cuadrícula.
4. El orden, la casilla "mostrar en el sitio" y el título e introducción de la sección no cambian.

**Criterios de aceptación**
- [ ] CA-35.1 Con 1, 2, 3 o 4 servicios la cuadrícula se ve bien en 360, 768, 1280 y 1920 px.
- [ ] CA-35.2 Un servicio sin imagen se ve completo (número, título, descripción y botón).

### RF-36 — Panel: "Servicios" e imagen de cada servicio

1. La entrada "Servicios (encabezado)" del panel pasa a llamarse **"Servicios"**.
2. Dentro, cada servicio tiene dos campos nuevos: **imagen** y **texto alternativo** de la imagen.
3. La imagen se valida y se optimiza igual que las demás del sitio (formato, tipo real, tamaño máximo, nombre nuevo al guardar).
4. La imagen es opcional (RF-35.3).

**Criterios de aceptación**
- [ ] CA-36.1 Subir o cambiar la imagen de un servicio se ve en el sitio al recargar.
- [ ] CA-36.2 Un archivo que no es una imagen válida se rechaza con un mensaje claro.
- [ ] CA-36.3 Un Viewer ve los servicios pero no puede cambiar su imagen.

### RF-37 — Descripción y "Cotizar" sobre la portada del servicio

1. Al pasar el cursor por la tarjeta de un servicio (o al llegar a ella con el teclado) aparece una capa oscura sobre la portada con la **descripción** del servicio y el botón **"Cotizar"**, que lleva al formulario.
2. La entrada es **suave**: la capa aparece con un fundido y su contenido sube unos píxeles mientras aparece. Ya no es un cambio seco de opacidad.
3. El texto del botón sigue saliendo del panel, y el botón no se muestra si la sección Contacto está oculta (como hoy).
4. Sustituye al botón "Cotizar" de RF-24, que iba debajo del texto de la tarjeta.

**Criterios de aceptación**
- [ ] CA-37.1 Con teclado se llega al botón de cada servicio y la capa se ve mientras tiene el foco.
- [ ] CA-37.2 Solo se animan `opacity` y `transform`.
- [ ] CA-37.3 Con "reducir movimiento", la capa aparece sin animación.

### RF-38 — Scroll discreto en la descripción de las tarjetas

1. Cuando la descripción no cabe en la capa, la barra de desplazamiento es **fina y del color del sitio**, no la del sistema.
2. Un **degradado en el borde inferior** avisa que el texto continúa.
3. Aplica a todas las capas con texto: tarjetas de proyecto, tarjetas de servicio y portada del detalle.

**Criterios de aceptación**
- [ ] CA-38.1 La barra fina se ve en Chrome, Edge, Firefox y Safari (en los que no la admitan, queda la del sistema: el texto se sigue pudiendo leer).
- [ ] CA-38.2 Al llegar al final, la última línea se lee completa.

### RF-39 — Descripción sobre la portada en el detalle del proyecto

1. En `/proyectos/<slug>`, al pasar el cursor por la portada aparece la capa con la descripción completa, igual que en las tarjetas (RF-22 y RF-38).
2. La descripción **se mantiene también debajo** de la portada: es donde se lee en celular y con lector de pantalla.

**Criterios de aceptación**
- [ ] CA-39.1 En escritorio, la capa aparece sobre la portada y no rompe el zoom ligado al scroll.
- [ ] CA-39.2 En celular la portada no lleva capa y la descripción se lee debajo.

### RF-40 — Ajustes del formulario

1. "Ubicación del espacio" tiene el **mismo ancho** que "Tipo de remodelación".
2. La casilla "Tengo fotos del espacio" va **arriba del mensaje**.
3. La tabla "Campos del formulario" del panel sigue ese mismo orden.

**Criterios de aceptación**
- [ ] CA-40.1 A 1280 px, Tipo y Ubicación miden lo mismo.
- [ ] CA-40.2 El orden en pantalla y al tabular es: …áreas, visita, estimado, fotos, mensaje, privacidad.

### RF-41 — Entradas suaves donde no hay cursor

1. En pantallas táctiles no existe "pasar el mouse". Ahí, lo que en escritorio depende del cursor **entra solo, con una animación suave, cuando la tarjeta aparece al hacer scroll**.
2. **Servicios:** la descripción y "Cotizar" entran sobre la portada.
3. **Proyectos:** la foto queda limpia; la categoría, el título y el resumen entran suaves debajo. La descripción completa se lee al abrir el proyecto.
4. Cada entrada ocurre una sola vez, y nada queda oculto si la animación no llega a ejecutarse (RF-06).

**Criterios de aceptación**
- [ ] CA-41.1 En un celular real, las tarjetas de servicio muestran descripción y botón sin tocar nada.
- [ ] CA-41.2 Con "reducir movimiento", todo se ve desde el principio, sin animación.

---

## 3. Qué deja de aplicar de lo anterior

| Antes | Qué pasa |
|---|---|
| RF-09.1 (specs-001): tarjetas de categorías en el inicio | Sustituido por RF-34: título y botón |
| Enlace a Instagram en la sección Proyectos (`specs/` S5) | Se quita (RF-34.4) |
| Casilla "usar como portada de su categoría" del proyecto | Deja de tener uso; se quita del formulario del panel y el dato se conserva |
| Servicios como tarjetas de texto sobre fondo claro (`specs/` S4) | Sustituido por RF-35: tarjetas con portada sobre fondo oscuro |
| RF-24 (specs-003): botón "Cotizar" debajo del texto | Sustituido por RF-37: dentro de la capa |
| P-25 (specs-003): "Cotizar" siempre visible en celular | Sustituido por RF-41: entra al aparecer la tarjeta |
| Orden de los campos del formulario de specs-003 | Cambia la posición de "Tengo fotos" (RF-40) |

---

## 4. Decisiones confirmadas

Respondidas por el desarrollador el 2026-10-09.

| # | Tema | Decisión |
|---|---|---|
| P-31 | Sección Proyectos del inicio | **Título + botón** |
| P-32 | Descripción en el detalle | **Al pasar el mouse**, y se mantiene debajo |
| P-33 | Tarjetas en celular | El contenido **entra al aparecer en pantalla** |
| P-34 | Scroll de la descripción | **Barra fina y discreta**, con degradado |
| P-35 | Servicio sin imagen | Fondo oscuro liso |
| P-36 | Números 01, 02… | Se conservan sobre la portada |
| P-37 | Texto del botón de Proyectos | Se reutiliza el campo del panel; cambia a "Ver proyectos" solo si seguía con el texto original |
| P-38 | "Usar como portada de su categoría" | Se quita del panel sin borrar el dato |
| P-39 | Portada del detalle en celular | Sin capa; la descripción va debajo |
| P-40 | "Reducir movimiento" | Todo lo nuevo aparece sin animación |
| P-41 | Forma de trabajo | **Por bloques, con una pausa de prueba al final de cada uno** |

---

## 5. Requisitos no funcionales

- RNF-14 Sin dependencias nuevas.
- RNF-15 Animaciones solo con CSS (`opacity` y `transform`), respetando `prefers-reduced-motion`.
- RNF-16 Todo lo nuevo se revisa a 360, 768, 1280 y 1920 px, y con teclado.
- RNF-17 Contraste suficiente del texto de las capas sobre cualquier foto.

---

## 6. Lo que sigue pendiente después de este paquete

- **Despliegue** (`specs/tasks.md`, Fase 5, T-5.1 a T-5.9): sin empezar. No se empieza sin que el desarrollador lo pida.
- **Textos legales:** los entrega el cliente o su abogado; hasta entonces, `[TEXTO PENDIENTE]`.
- **Imágenes de los servicios:** las carga el cliente desde el panel.

---

## 7. Fuera de alcance de specs-004

- Página propia para cada servicio.
- Varias imágenes por servicio.
- Cambios en el hero, el menú, el pie o el cálculo de la cotización.
