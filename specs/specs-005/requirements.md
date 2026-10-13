# Requisitos — specs-005: quinta ronda de cambios del cliente

> **Qué** cambia respecto a lo ya construido y **cómo sabemos que está bien hecho**.
> Es un paquete de cambios sobre `specs/` y los paquetes `specs-001` a `specs-004`. Donde este documento los contradice, **manda este**.

**Estado:** Implementado y cerrado (2026-10-13)
**Base:** `specs/` (RF-01 a RF-07) y `specs-001` a `specs-004` (RF-08 a RF-41), ya implementadas y cerradas.
**Reglas:** las mismas de `AGENTS.md`: mismo stack, mismos tokens de diseño, SDD, tests, accesibilidad y animaciones solo con CSS e `IntersectionObserver`.

> ⚠️ **El despliegue sigue pendiente y sin empezar.** Es la última fase del proyecto (`specs/tasks.md`, Fase 5) y viene después de este paquete. Ver §6.

---

## 1. Resumen de los cambios

| # | Pedido del cliente | Requisito |
|---|---|---|
| 1 | "Mostrar en el sitio" de las categorías es solo para lo que se ve; en el formulario siguen todas | RF-42 |
| 2 | Campos obligatorios del formulario | RF-43 (solo cambia Ubicación; el resto del pedido se descartó, ver P-42) |
| 3 | Servicios: que quepan hasta 4 tarjetas por fila | RF-44 |
| 4 | Detalle del proyecto: quitar la descripción de debajo de la portada (está duplicada) | RF-45 |
| 5 | Celular: que los textos sobre las portadas aparezcan parecido a como se ven en web | RF-46 |
| 6 | Celular: animaciones activas y suaves; algunas no se ven o son toscas | RF-47 |
| 7 | El encabezado se queda fijo al volver al inicio desde `/proyectos` con el logo | RF-48 |

**Se prueba por partes**, en tres bloques con pausa (ver `tasks.md`).

---

## 2. Requisitos funcionales

### RF-42 — "Mostrar en el sitio" de las categorías no afecta al formulario

1. La casilla "mostrar en el sitio" de una categoría decide solo si aparece en el **filtro de `/proyectos`**.
2. El "Tipo de remodelación" del formulario ofrece **todas** las categorías que tengan áreas, estén ocultas o no.
3. El backend acepta una cotización cuyo tipo es una categoría oculta.
4. El texto de ayuda de la casilla en el panel lo explica.

**Criterios de aceptación**
- [ ] CA-42.1 Con las tres categorías ocultas, el formulario sigue ofreciendo los tres tipos y se puede enviar una cotización.
- [ ] CA-42.2 Una categoría oculta sigue sin aparecer en el filtro de `/proyectos`.

### RF-43 — "Ubicación del espacio" es obligatoria

1. El campo "Ubicación del espacio" pasa a ser obligatorio, en el navegador y en el backend.
2. Los demás campos quedan como están (obligatorios: nombre, teléfono, correo, tipo, al menos un área y la aceptación de privacidad).
3. Las cotizaciones anteriores, que no tienen ubicación, se conservan.

**Criterios de aceptación**
- [ ] CA-43.1 Sin ubicación, el formulario muestra el error en ese campo y el backend responde `400`.

### RF-44 — Servicios: hasta cuatro tarjetas por fila

1. En escritorio, la sección Servicios muestra **hasta 4 tarjetas por fila**. Con menos de 4 servicios, se reparten el ancho entre los que haya (no queda un hueco).
2. En tableta van de 2 en 2 y en celular de una en una.
3. Con más de 4 servicios, los siguientes bajan a otra fila.

**Criterios de aceptación**
- [ ] CA-44.1 A 1280 y 1920 px, 4 servicios caben en una fila.
- [ ] CA-44.2 En la tarjeta más angosta, la descripción y "Cotizar" siguen leyéndose sin recortes (el texto se desplaza si no cabe).

### RF-45 — Detalle del proyecto sin descripción duplicada

1. En `/proyectos/<slug>` se quita el párrafo de descripción de debajo de la portada.
2. La descripción queda **solo en la capa** sobre la portada. Como es el único lugar donde se lee, deja de estar oculta a lectores de pantalla y se alcanza con teclado.
3. En celular la capa se muestra según RF-46.

**Criterios de aceptación**
- [ ] CA-45.1 La descripción aparece una sola vez en la página.
- [ ] CA-45.2 Con teclado se puede llegar a la portada, ver la capa y desplazar el texto.

### RF-46 — Celular: la capa aparece al centrarse la tarjeta

1. En pantallas táctiles, mientras se hace scroll, la tarjeta que **cruza el centro de la pantalla** muestra su capa con el mismo fundido que en web; al dejar de cruzarlo, la oculta.
2. Aplica a las tarjetas de servicio, a las tarjetas de proyecto y a la portada del detalle.
3. Sustituye a los comportamientos de specs-004 en táctil: la capa fija de los servicios y la entrada retrasada del texto de las tarjetas de proyecto.
4. Con "reducir movimiento", en táctil la capa de servicios y la del detalle se muestran fijas desde el principio (el texto no puede quedar inaccesible), y las tarjetas de proyecto quedan sin capa.

**Criterios de aceptación**
- [ ] CA-46.1 En un celular real, al bajar por Servicios cada tarjeta muestra su texto al llegar al centro y lo oculta al pasar.
- [ ] CA-46.2 Nunca hay dos capas activas a la vez.
- [ ] CA-46.3 En escritorio nada cambia: la capa sigue dependiendo del cursor y del teclado.

### RF-47 — Animaciones de entrada activas y suaves en móvil

1. Las entradas al hacer scroll (títulos, textos, botones y tarjetas) se ven en un celular: no terminan antes de que el elemento esté a la vista.
2. Usan la curva suave (`--ease-soft`) y un recorrido que se nota sin ser brusco.
3. Si el teléfono tiene activado "quitar animaciones" o el ahorro de batería, el sitio sigue sin animar: es lo correcto (RF-06).

**Criterios de aceptación**
- [ ] CA-47.1 Emulando un Android, cada entrada empieza con el elemento ya dentro de la pantalla.
- [ ] CA-47.2 El desarrollador confirma en su Android que las entradas se ven y son suaves.

### RF-48 — El encabezado vuelve a ocultarse y mostrarse tras navegar

1. Al volver al inicio con el logo desde `/proyectos` (con o sin filtro), el encabezado sigue ocultándose al bajar y mostrándose al subir.
2. Lo mismo tras cualquier otro cambio de página.

**Criterios de aceptación**
- [ ] CA-48.1 El caso se reproduce en una prueba de navegador antes del arreglo y deja de ocurrir después.

---

## 3. Qué deja de aplicar de lo anterior

| Antes | Qué pasa |
|---|---|
| RF-20 (specs-003): la categoría oculta sale también del formulario | Sustituido por RF-42 |
| RF-32 (specs-003): "Ubicación del espacio" opcional | Sustituido por RF-43 |
| Cuadrícula de Servicios igual a la de proyectos (specs-004, RF-35) | Sustituida por RF-44 |
| RF-39.2 (specs-004): la descripción se mantiene debajo de la portada | Sustituido por RF-45 |
| RF-41 (specs-004): en táctil el contenido entra al aparecer la tarjeta y se queda | Sustituido por RF-46 |

---

## 4. Decisiones confirmadas

| # | Tema | Decisión |
|---|---|---|
| P-42 | Campos obligatorios | El pedido de dejar solo nombre, tipo y ubicación **se descartó**: sin teléfono ni correo, RP Design no podría responder. Solo cambia Ubicación, que pasa a obligatoria |
| P-43 | Capas en celular | Aparecen **al centrarse la tarjeta en pantalla** |
| P-44 | Texto de las tarjetas de proyecto en celular | Queda fijo; no hay dos animaciones a la vez |
| P-45 | "Reducir movimiento" en táctil | Capa fija en servicios y detalle |
| P-46 | Campo "resumen" del proyecto | No se toca |
| P-47 | Forma de trabajo | Por bloques, con pausa de prueba |

---

## 5. Requisitos no funcionales

- RNF-18 Sin dependencias nuevas.
- RNF-19 Animaciones solo con CSS (`opacity` y `transform`) e `IntersectionObserver`; se respeta `prefers-reduced-motion`.
- RNF-20 Todo lo nuevo se revisa a 360, 768, 1280 y 1920 px, con teclado y en emulación táctil.

---

## 6. Lo que sigue pendiente después de este paquete

- **Despliegue** (`specs/tasks.md`, Fase 5, T-5.1 a T-5.9): sin empezar. No se empieza sin que el desarrollador lo pida.
- **Textos legales** e **imágenes de los servicios:** los entrega o carga el cliente.

---

## 7. Fuera de alcance de specs-005

- Cambiar qué otros campos del formulario son obligatorios.
- Cambios en el hero, el pie o el cálculo de la cotización.
