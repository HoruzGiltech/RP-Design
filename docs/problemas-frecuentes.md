# Problemas frecuentes y cómo resolverlos

> Errores que ya aparecieron trabajando en el proyecto, con su causa y su solución.
> Si aparece uno nuevo, se agrega aquí con el mismo formato.

Los comandos se ejecutan desde la carpeta del proyecto (o cualquiera de sus subcarpetas).

## Diagnóstico rápido

Antes de buscar el error en la lista, mira en qué estado están los contenedores:

```bash
docker compose ps -a
```

| Lo que ves | Qué significa | Qué hacer |
|---|---|---|
| `Up` en `db` y `backend` | Todo está encendido | El problema es otro: mira los registros con `docker compose logs --tail 30 backend` |
| `Exited` | Los contenedores existen pero están apagados | `docker compose up -d` |
| Lista vacía | Nunca se crearon o se borraron | `docker compose up --build -d` |
| Error de conexión con Docker | Docker Desktop está cerrado | Ver el problema 2 |

---

## 1. `service "backend" is not running`

**Cuándo aparece:** al ejecutar cualquier `docker compose exec backend ...` (tests, `migrate`, `createsuperuser`).

**Causa:** los contenedores están apagados. Pasa cada vez que se cierra Docker Desktop o se apaga la computadora: los contenedores no vuelven a encenderse solos.

**Solución:**

```bash
docker compose up -d
```

Espera a que termine y repite el comando que falló. La opción `-d` deja los contenedores funcionando en segundo plano, sin ocupar la terminal.

**No se pierde nada:** la base de datos, los usuarios y los archivos subidos siguen ahí, porque viven en volúmenes de Docker. Solo se borrarían con `docker compose down -v`.

## 2. `failed to connect to the docker API ... dockerDesktopLinuxEngine`

**Cuándo aparece:** con cualquier comando `docker`.

**Causa:** Docker Desktop no está abierto, o se abrió hace unos segundos y todavía está arrancando.

**Solución:** abre Docker Desktop desde el menú de inicio y espera a que el motor esté en marcha (tarda cerca de un minuto). Después ejecuta `docker compose up -d`.

## 3. El panel no acepta el usuario y la contraseña

**Cuándo aparece:** en `http://localhost:8000/panel-rp/`, con el mensaje de que el usuario o la contraseña no son correctos.

**Causa A: se usaron los datos de la base de datos.** `POSTGRES_USER` y `POSTGRES_PASSWORD` del archivo `.env` (`rp` / `rp`) son para que Django se conecte a Postgres. No sirven para entrar al panel.

**Causa B: todavía no hay ningún usuario del panel.** Se crea con:

```bash
docker compose exec backend python manage.py createsuperuser
```

**Causa C: la contraseña quedó distinta a la que se cree.** Al escribirla en la terminal no se ve nada en pantalla, y es fácil equivocarse. Se cambia con:

```bash
docker compose exec backend python manage.py changepassword admin
```

(`admin` es el nombre del usuario. El panel distingue mayúsculas de minúsculas.)

**Para ver qué usuarios existen:**

```bash
docker compose exec backend python manage.py shell -c "from django.contrib.auth import get_user_model; print(list(get_user_model().objects.values_list('username', flat=True)))"
```

## 4. `relation "core_samplesingleton" already exists` al ejecutar los tests

**Causa:** una app de Django que no tiene carpeta `migrations/`. En ese caso Django crea las tablas de la app por su cuenta al preparar la base de pruebas, incluida la del modelo que el test intenta crear después.

**Solución:** toda app del proyecto debe tener la carpeta `migrations/` con un archivo `__init__.py` vacío, aunque todavía no tenga migraciones.

## 5. Aviso `No directory at: /app/staticfiles/` en los tests

**Causa:** whitenoise busca la carpeta donde `collectstatic` reúne los archivos estáticos, y en local esa carpeta no existe.

**Solución:** ninguna. Es un aviso, no un error, y los tests pasan igual. Deja de salir si se ejecuta `docker compose exec backend python manage.py collectstatic`.

## 6. `GET /static/adminsortable2/js/actions-6.1.js ... 404` en los registros del backend

**Cuándo aparece:** al abrir en el panel una lista que se ordena arrastrando (Proyectos, Áreas y precios, Servicios...).

**Causa:** `django-admin-sortable2` 2.3.1 trae ese archivo solo hasta Django 6.0. El proyecto arrancó con Django 6.1.

**Efecto:** arrastrar para ordenar funcionaba, pero en esas listas fallaban la casilla "seleccionar todo" y el contador de elementos seleccionados.

**Solución (aplicada el 2026-10-06):** se fijó Django en la versión 5.2 LTS en `backend/requirements.txt`. Si el error vuelve a aparecer con otro número (por ejemplo `actions-6.0.js`), es que alguien subió Django a una versión que la librería todavía no soporta: antes de actualizar Django hay que revisar qué archivos `actions-X.Y.js` trae la librería.

## 7. La API responde `429` ("demasiadas peticiones")

**Cuándo aparece:** al enviar más de 5 cotizaciones en una hora desde la misma computadora, o más de 120 peticiones por minuto al resto de la API. Es fácil llegar al primero haciendo pruebas.

**Causa:** es el límite de seguridad, funcionando como debe.

**Solución en local:** reiniciar el backend borra los contadores:

```bash
docker compose restart backend
```

Los límites se cambian en `.env` (`THROTTLE_PUBLIC` y `THROTTLE_QUOTES`).

## 8. El panel muestra "Demasiados intentos" y no deja entrar

**Cuándo aparece:** después de 5 intentos fallidos de login desde el mismo equipo. El bloqueo dura 30 minutos.

**Causa:** es la protección contra robo de contraseñas (`django-axes`), funcionando como debe. Se bloquea el equipo (su dirección IP), no el usuario.

**Solución:** esperar 30 minutos, o quitar el bloqueo a mano:

```bash
docker compose exec backend python manage.py axes_reset
```

Si el problema era la contraseña, se cambia como explica el problema 3.

## 9. `ImproperlyConfigured: DJANGO_SECRET_KEY sigue con el valor de ejemplo`

**Cuándo aparece:** al arrancar el backend con `DJANGO_DEBUG=False`.

**Causa:** en modo producción el proyecto se niega a arrancar con la clave `cambia-esto` de `.env.example`, porque con una clave conocida cualquiera podría falsificar sesiones del panel.

**Solución:** generar una clave y ponerla en `DJANGO_SECRET_KEY`:

```bash
docker compose exec backend python -c "import secrets; print(secrets.token_urlsafe(64))"
```

En local no hace falta: con `DJANGO_DEBUG=True` la clave de ejemplo se acepta.

---

## Cómo agregar un problema nuevo

Copia este bloque al final de la lista:

```markdown
## N. Mensaje de error tal como aparece

**Cuándo aparece:** qué comando o acción lo provoca.

**Causa:** por qué pasa.

**Solución:** los comandos o pasos exactos.
```
