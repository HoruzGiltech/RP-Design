# Requisitos — specs-011: video de fondo en la sección Proceso

> **Qué** se construye. Noveno paquete de cambios del cliente.

**Estado:** Implementado y cerrado (2026-10-16), incluido RF-70

**Reglas:** las mismas de `AGENTS.md`. Este paquete solo describe lo que cambia; lo demás sigue como en `specs/` y en los paquetes anteriores.

---

## 1. Resumen

| # | Pedido | Requisito |
|---|---|---|
| 1 | El video de la sección Proceso ("Un solo equipo para todo tu proyecto") deja de ser un recuadro con controles: pasa a ser el **fondo de toda la sección** | RF-68 |
| 2 | El video se reproduce **solo**, apenas carga la sección, **sin sonido** y **sin botones visibles** | RF-69 |
| 3 | Al ocultar todas las tarjetas del proceso, la sección desaparece entera aunque "Mostrar en el sitio" esté marcado y haya video. Debe seguir viéndose con el título, la introducción y el video | RF-70 |

Es el video que hoy se ve en la sección **Proceso** como un recuadro con controles (reproducir, tiempo, volumen, pantalla completa) debajo del título "Un solo equipo para todo tu proyecto". Se carga en el panel, en **Proceso**. La sección **Proyectos** no cambia: solo se reutiliza el código que ya hace su fondo (specs-009).

---

## 2. Requisitos funcionales

### RF-68 — El video como fondo de la sección Proceso

1. El video cubre **toda la sección**, de borde a borde y de arriba abajo: detrás del título, la introducción y las tarjetas numeradas.
2. Lleva encima una capa oscura, como el fondo de Proyectos (specs-009), para que el texto se lea sobre cualquier imagen del video.
3. Con el video de fondo, el título y la introducción pasan a blanco, y las tarjetas se ven oscuras y semitransparentes, con el texto y el número en blanco (ver P-71).
4. El video se recorta para llenar la sección sin deformarse (`object-fit: cover`), en escritorio y en celular.
5. Sin video cargado, o con la casilla **"Mostrar el video"** desmarcada (RF-59), la sección se ve **como hoy**: fondo claro y tarjetas con contorno.
6. La "vista previa del video" del panel se usa como imagen mientras el video carga.

**Criterios de aceptación**
- [ ] CA-68.1 Con video y casilla marcada, el video ocupa toda la sección, detrás del texto y las tarjetas, sin franjas vacías a los lados ni arriba o abajo.
- [ ] CA-68.2 El título, la introducción y las tarjetas se leen bien sobre el video (contraste suficiente).
- [ ] CA-68.3 En el celular el video llena la sección sin deformarse y no aparece barra de desplazamiento horizontal.
- [ ] CA-68.4 Al desmarcar la casilla, la sección vuelve a verse como hoy, sin borrar el video.

### RF-69 — Reproducción automática, sin sonido y sin controles

1. El video empieza solo, sin que el visitante haga nada.
2. Se reproduce **sin sonido** y **en bucle** (al terminar vuelve a empezar; ver P-70).
3. **No se ve ningún botón**: ni reproducir, ni pausa, ni volumen, ni pantalla completa. Tampoco aparecen al pasar el cursor ni al tocarlo en el celular.
4. Es decoración: los lectores de pantalla lo ignoran (el título ya dice de qué trata la sección).
5. Con **"reducir movimiento"** activo en el sistema, no se reproduce: se muestra fija la vista previa del video. Si no hay vista previa, la sección se ve como hoy (fondo claro). Así se cumple RF-06: nada se mueve solo para quien lo pidió.

**Criterios de aceptación**
- [ ] CA-69.1 Al llegar a la sección, el video ya se está reproduciendo, también en el celular (iPhone y Android).
- [ ] CA-69.2 No suena nada, aunque el archivo subido tenga audio.
- [ ] CA-69.3 No hay controles visibles en ningún momento, ni con el cursor encima ni al tocarlo.
- [ ] CA-69.4 Con "reducir movimiento" activo, el video no se reproduce y se ve la imagen fija.

### RF-70 — La sección Proceso se muestra sin tarjetas si tiene video

Hasta ahora la sección se ocultaba entera si no había pasos visibles (specs-008), para no dejar un título suelto. Con el video de fondo, la sección tiene contenido propio aunque no haya tarjetas.

1. Con **"Mostrar en el sitio"** marcado, la sección se muestra si tiene **al menos un paso visible o un fondo** (el video, o su vista previa con "reducir movimiento").
2. Sin pasos visibles y con fondo, se ven el título, la introducción y el video, sin la cuadrícula vacía.
3. Sin pasos visibles y sin fondo, la sección sigue sin mostrarse (no se deja un título suelto sobre fondo claro).
4. Con **"Mostrar en el sitio"** desmarcado, la sección no se muestra, tenga lo que tenga.
5. Sin tarjetas, la sección no queda como una franja angosta: tiene una altura mínima para que el video se luzca, como el fondo de Proyectos (60 % de la pantalla; 50 % en el celular), con el título centrado en vertical.

**Criterios de aceptación**
- [ ] CA-70.1 Con todos los pasos ocultos, video cargado y las dos casillas marcadas, se ven el título, la introducción y el video.
- [ ] CA-70.2 Con todos los pasos ocultos y sin video (o con "Mostrar el video" desmarcada), la sección no aparece.
- [ ] CA-70.3 Con "Mostrar en el sitio" desmarcado, la sección no aparece.
- [ ] CA-70.4 Al volver a mostrar los pasos, las tarjetas aparecen como antes.

---

## 3. Lo que no cambia

- Los campos del panel de "Proceso": el video, su vista previa y la casilla "Mostrar el video" (RF-59). Solo cambian sus nombres y textos de ayuda, para que digan que ahora es un fondo.
- El título, la introducción y los pasos, y cómo se editan.
- El orden de las secciones del inicio y el menú.
- El fondo de la sección Proyectos (specs-009).

---

## 4. Decisiones propuestas (revisar)

| # | Tema | Propuesta | Motivo |
|---|---|---|---|
| P-70 | Al terminar el video | Vuelve a empezar (bucle) | Un fondo que se detiene en el último cuadro parece un error |
| P-71 | Las tarjetas sobre el video | Oscuras y semitransparentes, con texto y número en blanco (el acento de la maqueta es casi negro y no se vería) | Unas tarjetas blancas taparían casi todo el video; unas transparentes del todo no se leerían |
| P-72 | Cuándo empieza | Apenas carga la página, como el fondo de Proyectos | Es lo más simple y fiable; el bucle hace que se vea en movimiento cuando la persona llega a la sección |
| P-73 | Sonido del archivo | Se silencia siempre en el sitio; no hace falta quitarle el audio al subirlo | Los navegadores solo reproducen solos los videos sin sonido |
| P-74 | Peso del video | Misma regla de siempre (≤ 50 MB), con la ayuda del panel pidiendo un video corto y comprimido | Un fondo pesado hace lenta la página en el celular |
| P-75 | Dónde va RF-70 | En este mismo paquete, reabierto, y no en un specs-012 | Es un ajuste del cambio que se acaba de publicar, no un pedido nuevo |
