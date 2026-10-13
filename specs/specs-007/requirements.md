# Requisitos — specs-007: subir archivos en el panel sin perder lo ya elegido

> **Qué** cambia en el panel y **cómo sabemos que está bien hecho**.
> Es un paquete de cambios sobre `specs/` y los paquetes anteriores. Donde este documento los contradice, **manda este**.

**Estado:** Implementado y cerrado (2026-10-13)
**Reglas:** las mismas de `AGENTS.md`. Sin dependencias nuevas.

> ⚠️ El **despliegue definitivo** sigue pendiente (`specs/tasks.md`, Fase 5). La demo de `specs/specs-006/` está publicada; este paquete se sube también a la demo.

---

## 1. El problema

Al guardar un proyecto con varias fotos, si una sola pasa de 5 MB el formulario vuelve con el error y **todas** las fotos elegidas se pierden. Es una limitación de los navegadores: por seguridad, el servidor no puede volver a rellenar los campos de archivo. Además, cada foto de la galería exigía escribir su texto alternativo, otro motivo frecuente de error.

| # | Pedido | Requisito |
|---|---|---|
| 1 | Que un archivo demasiado pesado no borre los demás que ya se eligieron | RF-56 |
| 2 | Que el texto alternativo de las imágenes se ponga solo | RF-57 |

---

## 2. Requisitos funcionales

### RF-56 — Los archivos se revisan al elegirlos

1. En el panel, al elegir un archivo en cualquier campo de subida, el navegador comprueba **en ese momento** su formato y su tamaño.
2. Si no cumple, se muestra el motivo junto al campo y **solo ese campo** se vacía. Los demás archivos elegidos y los textos escritos no se tocan.
3. Los mensajes dicen qué pasa y qué hacer: *"Esta foto pesa 7,2 MB. El máximo es 5 MB."* o *"Formato no permitido. Usa: jpg, jpeg, png, webp."*
4. Los formatos y los tamaños son los mismos que valida el servidor y salen de la misma configuración (`MAX_IMAGE_MB`, `MAX_VIDEO_MB`, `MAX_FONT_MB`).
5. Aplica a todos los campos de archivo del panel: portada y galería de los proyectos, imágenes de los servicios, Portada, Proceso, logo y fuentes. También a las filas de galería que se agregan con "Agregar otro".
6. La validación del servidor **no cambia**: sigue siendo la que manda (el navegador no detecta, por ejemplo, un programa renombrado como `.jpg`).

**Criterios de aceptación**
- [ ] CA-56.1 En un proyecto, con tres fotos válidas elegidas, elegir una cuarta de más de 5 MB muestra el aviso, vacía solo ese campo y conserva las otras tres.
- [ ] CA-56.2 Al elegir después un archivo válido en ese campo, el aviso desaparece.
- [ ] CA-56.3 Un video de hasta 50 MB se acepta en la galería; una imagen de 6 MB, no.
- [ ] CA-56.4 Si el navegador tiene JavaScript desactivado, el panel funciona como antes.

### RF-57 — Texto alternativo automático

1. El texto alternativo deja de ser obligatorio en la **portada** y en la **galería** de los proyectos.
2. Si se deja vacío, se completa solo al guardar:
   - Galería: el nombre del proyecto y un número correlativo de tres cifras, por ejemplo **"Apto La Guaira 001"**, "Apto La Guaira 002"…
   - Portada: el nombre del proyecto.
   - Imagen de un servicio: el nombre del servicio.
3. Si el cliente escribe un texto, se respeta el suyo.
4. Los textos ya guardados no cambian.

**Criterios de aceptación**
- [ ] CA-57.1 Un proyecto se guarda con varias fotos sin escribir ningún texto alternativo, y cada una queda con el suyo.
- [ ] CA-57.2 El número sigue el orden en que se agregan las fotos al proyecto.
- [ ] CA-57.3 Un texto escrito por el cliente no se reemplaza.

---

## 3. Qué deja de aplicar de lo anterior

| Antes | Qué pasa |
|---|---|
| Texto alternativo obligatorio en portada y galería (`specs/`, RF-02 y §7) | Sustituido por RF-57: opcional, con valor automático |

---

## 4. Decisiones confirmadas

| # | Tema | Decisión |
|---|---|---|
| P-52 | Cómo evitar perder los archivos | Revisarlos en el navegador al elegirlos. No se guardan archivos temporales en el servidor ni se agrega una librería |
| P-53 | Texto alternativo | Automático, con el nombre del proyecto y un correlativo |
| P-54 | Formato del texto | **"Apto La Guaira 001"** (el nombre tal como se escribió, no con guiones): es lo que un lector de pantalla dice en voz alta |

---

## 5. Lo que este paquete no cubre

Si el formulario falla por un motivo que solo el servidor detecta (un archivo dañado, o un programa renombrado como imagen), los archivos elegidos se siguen perdiendo. Es poco frecuente; resolverlo exigiría guardar archivos temporales en el servidor.
