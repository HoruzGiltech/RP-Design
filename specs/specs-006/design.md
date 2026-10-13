# Diseño — specs-006: publicación temporal (demo)

> **Cómo** se construyen los requisitos de `specs/specs-006/requirements.md`.

**Estado:** Aprobado (v1, 2026-10-13)

---

## 1. Qué se toca

| Bloque | Archivos |
|---|---|
| **1. Backend listo para producción** (RF-49 a RF-51) | `backend/Dockerfile`, `backend/requirements.txt`, `docker-compose.yml`, `backend/config/settings.py`, `backend/config/urls.py`, `backend/core/network.py` (nuevo), `backend/core/views.py` (nuevo), `.env.example` |
| **2. Frontend y guía** (RF-52, RF-53, RF-55) | `frontend/vercel.json` (nuevo), `frontend/index.html`, `frontend/.env.example`, `docs/despliegue-demo.md` (nuevo) |
| **3. Publicación** (RF-54) | Sin código previsto: copia del contenido y prueba del sitio publicado |

Única dependencia nueva: `gunicorn` (el servidor de producción estándar de Django; ya estaba previsto en `specs/tasks.md` T-5.3).

---

## 2. Backend (bloque 1)

### 2.1 Servidor de producción (RF-49)

- `requirements.txt`: `gunicorn==26.2.0`.
- `Dockerfile`: el comando por defecto pasa a ser el de producción:
  ```dockerfile
  CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120"]
  ```
  Va escrito en el propio `Dockerfile`, sin un archivo `.sh` aparte, para que haya un solo lugar que mirar.
- `docker-compose.yml`: el servicio `backend` fija `command: python manage.py runserver 0.0.0.0:8000`. Así en local sigue el servidor de desarrollo.
- `--timeout 120`: subir un video de 50 MB tarda más que los 30 s por defecto.

### 2.2 Archivos subidos (RF-50)

- `settings.py`: `SERVE_MEDIA = env.bool("SERVE_MEDIA", default=DEBUG)`.
- `core/views.py`: `serve_media(request, path)`. Responde 404 si `SERVE_MEDIA` es falso; si no, delega en `django.views.static.serve` con `document_root=settings.MEDIA_ROOT`. Esa función de Django ya impide salir de la carpeta.
- `urls.py`: la ruta `media/<path>` queda siempre registrada y apunta a esa vista (antes solo existía con `DEBUG`).
- En Railway el volumen se monta en `/app/media`, que es `MEDIA_ROOT`.

### 2.3 IP real (RF-51)

- `settings.py`: `NUM_PROXIES = env.int("NUM_PROXIES", default=0)`, que también se pasa a `REST_FRAMEWORK["NUM_PROXIES"]` (DRF ya sabe usarlo para sus límites).
- `core/network.py`: `get_client_ip(request)`, con la misma regla que DRF: con 0 proxies usa `REMOTE_ADDR`; con N, toma de `X-Forwarded-For` la dirección que puso el proxy de confianza (la N-ésima desde el final).
- `settings.py`: `AXES_CLIENT_IP_CALLABLE = "core.network.get_client_ip"`, para que el bloqueo del panel use la misma IP.

> Hoy `NUM_PROXIES` no está definido, y en ese caso DRF usa `X-Forwarded-For` tal como llega: cualquiera podría saltarse el límite de cotizaciones inventando esa cabecera. Con el valor 0 por defecto eso queda cerrado también en local.

`FRONTEND_URL` aparece en `.env.example` pero el backend no la usa: no hace falta definirla en Railway.

### 2.4 Variables nuevas (`.env.example`)

```
SERVE_MEDIA=True      # solo hace falta en producción con volumen; en local se sirve siempre
NUM_PROXIES=0         # 1 en Railway
```

### 2.5 Tests

- `get_client_ip`: sin proxies ignora la cabecera; con 1 y con 2 proxies elige la dirección correcta; cabecera ausente o más corta de lo esperado.
- Límite de cotizaciones: con `NUM_PROXIES=0`, cambiar `X-Forwarded-For` no da intentos extra; con `NUM_PROXIES=1`, dos direcciones distintas tienen límites separados.
- `serve_media`: entrega un archivo con `SERVE_MEDIA=True`; 404 con `False`; 404 para una ruta que intenta salir de la carpeta.

---

## 3. Frontend (bloque 2)

- `frontend/vercel.json`:
  ```json
  { "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }] }
  ```
  Vercel entrega primero los archivos que existen (JS, CSS, fuentes) y solo usa esta regla para lo demás.
- `frontend/index.html`: `<meta name="robots" content="%VITE_ROBOTS%" />`. Vite sustituye el valor al construir.
- `frontend/.env.example`: `VITE_ROBOTS=index, follow`. En Vercel se pone `noindex, nofollow`.
- En Vercel: carpeta raíz `frontend`, comando `npm run build`, salida `dist`.
- Si `VITE_ROBOTS` no está definida, Vite deja el texto `%VITE_ROBOTS%` sin sustituir; los buscadores lo ignoran y el sitio se indexa normalmente. Por eso la variable va en `frontend/.env.example` y en la guía.

---

## 4. Copia del contenido (bloque 3)

1. **Datos:** `manage.py dumpdata` de `projects`, `site_content` y `quotes.RemodelArea` a un archivo fuera del repositorio; `loaddata` contra la base de Railway. Las migraciones de la demo ya crean las filas iniciales; `loaddata` las reemplaza por las locales.
2. **Archivos (14 MB, 81 archivos):** comando `manage.py transfer_media` (`core/management/commands/`). Al volumen de Railway no se le pueden copiar archivos desde una computadora, así que se usa la base de datos como transporte: `transfer_media pack`, ejecutado en local contra la base de Railway, empaqueta `media/` en una tabla temporal; `transfer_media unpack`, ejecutado en la consola del servicio en Railway, extrae los archivos al volumen y borra la tabla. Así no hace falta instalar la CLI de Railway. Tiene tests de ida y vuelta.
3. **Usuarios:** `createsuperuser` en Railway para el desarrollador; el del cliente se crea desde el panel con el grupo Admin.

---

## 5. Registro de decisiones

| Decisión | Motivo |
|---|---|
| El comando de producción es el que trae la imagen; el de desarrollo lo pone `docker-compose.yml` | Railway usa la imagen tal cual, sin configuración extra |
| Vista propia `serve_media` en vez de `static()` | `static()` solo funciona con `DEBUG`; y así se puede probar con y sin la variable |
| `NUM_PROXIES=0` por defecto | Es el valor seguro: sin proxy de confianza no se cree en ninguna cabecera |
| `dumpdata`/`loaddata` en vez de copiar la base entera | Deja fuera cotizaciones, usuarios y registros sin tener que borrarlos después |

---

## 6. Riesgos

- **Videos en iPhone** (Safari pide los videos por partes y Django no lo hace): limitación aceptada de la demo.
- **Subida de archivos al volumen:** paso sin confirmar (ver §4).
- **Dos trabajadores de gunicorn y un volumen:** suficiente para una demo; no está pensado para mucho tráfico.
