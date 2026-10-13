# Diseño — specs-007

> **Cómo** se construyen los requisitos de `specs/specs-007/requirements.md`.

**Estado:** Implementado y cerrado (2026-10-13)

---

## 1. Qué se toca

| Requisito | Archivos |
|---|---|
| RF-56 | `backend/core/validators.py` (`get_upload_rules`), `backend/core/admin_mixins.py` (nuevo), `backend/core/static/core/admin-file-check.js` (nuevo), y los `admin.py` de `projects` y `site_content` |
| RF-57 | `backend/projects/models.py`, `backend/projects/services.py`, `backend/site_content/models.py`, migración `projects.0007` |

Solo backend. El sitio público no cambia.

---

## 2. Revisión de archivos en el navegador (RF-56)

### 2.1 De dónde salen las reglas

Cada campo de archivo ya tiene su validador (`validate_image_file`, `validate_video_file`, `validate_media_file` o `validate_font_file`). Una función nueva traduce ese validador a una tabla "extensión → tamaño máximo en MB":

```python
# core/validators.py
def get_upload_rules(validator):
    """validate_media_file -> {"jpg": 5, "png": 5, ..., "mp4": 50, "webm": 50}"""
```

Se calcula al pedir la página, leyendo `settings.MAX_IMAGE_MB` y compañía: si el límite cambia en `.env`, el navegador usa el nuevo valor sin tocar código.

### 2.2 Cómo llegan al navegador

`core/admin_mixins.py`: `FileCheckMixin`, para clases del panel y sus tablas internas.

- Sobrescribe `formfield_for_dbfield`: a cada campo de archivo le pone el atributo `data-upload-rules='{"jpg": 5, ...}'` en su `<input>`.
- Su clase `Media` carga `core/admin-file-check.js`.

Lo usan `ProjectAdmin`, `ProjectMediaInline`, `SingletonAdmin` (y con él todas las secciones) y `SectionItemInline` (servicios y pasos).

### 2.3 El script (`admin-file-check.js`)

JavaScript sin librerías, unas 60 líneas:

1. Escucha el evento `change` en todo el documento (así cubre también las filas que se agregan después).
2. Si el campo tiene `data-upload-rules` y un archivo elegido: toma la extensión y busca su límite.
3. Sin límite para esa extensión → "Formato no permitido. Usa: …". Con límite y tamaño mayor → "Este archivo pesa X MB. El máximo es Y MB."
4. Con error: vacía ese campo (`input.value = ""`) y muestra el mensaje en una lista `errorlist`, la misma clase que usa el panel para sus errores. Sin error: quita el mensaje anterior.

Los estáticos del panel los sirve Whitenoise; en la demo se recogen solos al arrancar (`collectstatic`).

---

## 3. Texto alternativo automático (RF-57)

- `projects/services.py`: `build_media_alt(project_title, number)` → `"Apto La Guaira 001"`.
- `ProjectMedia.alt_text` y `Project.cover_alt` pasan a `blank=True`, con una ayuda que explica que se completan solos. Migración `projects.0007`.
- `ProjectMedia.save()`: si `alt_text` está vacío, lo completa. El número es la cantidad de archivos que ya tiene el proyecto más uno.
- `Project.save()`: si `cover_alt` está vacío, usa el título.
- `Service.save()`: si hay imagen y `image_alt` está vacío, usa el título del servicio. (El campo ya era opcional.)

---

## 4. Tests

- `get_upload_rules`: imagen, video, galería (ambos) y fuente; respeta un límite cambiado con `override_settings`.
- Panel: el formulario de proyecto trae `data-upload-rules` en la portada y en la galería y carga el script; "Configuración general" lo trae en las fuentes.
- `build_media_alt` y los tres `save()`: vacío se completa, escrito se respeta, el correlativo avanza.
- El script se verifica en el navegador con Playwright (CA-56.1 a CA-56.3); no hay herramientas de test de JavaScript para el panel y no se agregan por 60 líneas.

---

## 5. Registro de decisiones

| Decisión | Motivo |
|---|---|
| Las reglas viajan en un atributo de cada campo | El script no necesita saber qué campo es: lee su propia regla. Y no hace falta sobrescribir plantillas del panel |
| Las reglas se derivan de los validadores | Una sola fuente de verdad: navegador y servidor no pueden desincronizarse |
| El correlativo es "los que hay más uno" | Simple. Si se borra una foto y se sube otra puede repetirse un número; el texto alternativo no necesita ser único |
