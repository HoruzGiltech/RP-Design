# Requisitos — specs-009: imagen o video de fondo en la sección Proyectos

> **Qué** se construye. Séptimo paquete de cambios del cliente.

**Estado:** Aprobado (v1, 2026-10-14)

**Reglas:** las mismas de `AGENTS.md`. Este paquete solo describe lo que cambia; lo demás sigue como en `specs/` y en los paquetes anteriores.

---

## 1. Resumen

| # | Pedido del cliente | Requisito |
|---|---|---|
| 1 | En la sección Proyectos del inicio (la franja negra con el título, el enlace a Instagram y el botón "Ver proyectos"), poder poner una imagen o un video de fondo a todo el ancho, tipo hero | RF-65 |
| 2 | Poder mostrarlo u ocultarlo desde el panel sin borrarlo | RF-66 |

---

## 2. Requisitos funcionales

### RF-65 — Fondo de la sección Proyectos

- En el panel, **Proyectos (encabezado)** gana tres campos opcionales: **imagen de fondo**, **texto alternativo** y **video de fondo**.
- La imagen o el video ocupan **todo el ancho y el alto** de la sección. El título, el enlace a Instagram y el botón quedan **encima**, sobre una capa oscura que mantiene el texto legible.
- Si hay **video**, se muestra el video: en bucle, sin sonido y sin controles. La imagen sirve de vista previa mientras carga.
- Si solo hay **imagen**, se muestra la imagen fija.
- Con **"reducir movimiento"** activo en el sistema, el video no se reproduce: se ve la imagen, o el fondo negro si no hay imagen.
- Formatos y tamaños: los mismos de siempre (RF-02 y specs-007). Imagen `jpg`, `jpeg`, `png` o `webp` de hasta 5 MB, optimizada al guardar; video `mp4` o `webm` de hasta 50 MB.
- La sección queda algo más alta que hoy, para que el fondo se luzca, pero no ocupa la pantalla completa como el hero.

**Criterios de aceptación**
- [ ] CA-65.1 Con imagen y sin video, la sección muestra la imagen de fondo a todo el ancho, con el texto encima y legible.
- [ ] CA-65.2 Con video, se reproduce solo, en bucle y sin sonido. Con "reducir movimiento" no se reproduce y se ve la imagen.
- [ ] CA-65.3 Sin imagen ni video, la sección se ve exactamente como hoy (negra).
- [ ] CA-65.4 En el celular el fondo cubre la sección sin deformarse y el botón sigue a la vista.
- [ ] CA-65.5 La imagen lleva su texto alternativo. Si está vacío, el fondo se trata como decorativo (`alt=""`), porque el título ya describe la sección.

### RF-66 — Mostrar u ocultar el fondo

- Casilla **"Mostrar la imagen o el video de fondo"** en Proyectos (encabezado). Viene **desmarcada**, para que el sitio no cambie hasta que el cliente lo decida.
- Desmarcada, la sección vuelve al fondo negro y **los archivos no se borran**.
- Es independiente de "Mostrar en el sitio", que oculta la sección entera.

**Criterios de aceptación**
- [ ] CA-66.1 Con la casilla desmarcada, el sitio no descarga ni la imagen ni el video.
- [ ] CA-66.2 Marcada pero sin archivos, la sección se ve negra, sin un bloque roto.

---

## 3. Lo que no cambia

- El título, el enlace a Instagram, el botón y sus animaciones de entrada (RF-34, RF-64).
- La página `/proyectos` y su encabezado.
- El orden de las secciones del inicio.

---

## 4. Decisiones confirmadas (2026-10-14)

| # | Tema | Decisión |
|---|---|---|
| P-61 | Dónde | Solo en la sección Proyectos del inicio |
| P-62 | Distribución | Imagen o video de fondo, con el texto encima sobre una capa oscura |
| P-63 | Imagen y video a la vez | Se muestra el video; la imagen es su vista previa y el respaldo con "reducir movimiento" |

## 5. Decisiones propuestas (revisar)

| # | Tema | Propuesta | Motivo |
|---|---|---|---|
| P-64 | Valor inicial de la casilla | Desmarcada | El sitio publicado no cambia hasta que el cliente suba el archivo y la active |
| P-65 | Alto de la sección | Con fondo, mínimo 60 % de la pantalla en escritorio y 50 % en el celular; nunca pantalla completa | Que el fondo se aprecie sin competir con el hero |
| P-66 | Movimiento | Sin zoom ni parallax en el fondo; solo el video, si lo hay | Simple y liviano en el celular |
