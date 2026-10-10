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

## 10. El sitio no carga desde otro equipo o el celular (o deja de cargar de un día para otro)

**Cuándo aparece:** al abrir `http://<IP-de-la-computadora>:5173/` desde el celular, o cuando el sitio se queda en "Cargando…" o muestra "No pudimos conectar con el servidor".

**Causa:** para probar desde el celular, la IP de la computadora en la red local está escrita en dos archivos: `.env` (`DJANGO_ALLOWED_HOSTS` y `CORS_ALLOWED_ORIGINS`) y `frontend/.env` (`VITE_API_URL`). El router puede asignar otra IP al reiniciarse, y entonces esos archivos apuntan a una dirección que ya no existe.

**Solución:**

1. Mira la IP actual con `ipconfig` (línea "Dirección IPv4" del adaptador Wi-Fi).
2. Cámbiala en los dos archivos.
3. Recrea los contenedores para que lean los archivos nuevos:

```bash
docker compose up -d --force-recreate backend frontend
```

Para trabajar solo en la computadora, se puede volver a `http://localhost:8000/api` en `frontend/.env`.

Si la IP es correcta y aun así el celular no abre el sitio, revisa que la VPN esté pausada y que el firewall de Windows permita Docker en redes privadas.

## 11. `npm run lint` falla con `Cannot find native binding`

**Cuándo aparece:** al ejecutar `cd frontend && npm run lint` directamente en Windows.

**Causa:** oxlint necesita un archivo distinto para cada sistema operativo, y en `frontend/node_modules` de la computadora falta el de Windows (es un fallo conocido de npm con las dependencias opcionales).

**Solución:** ejecutar el linter dentro del contenedor, que sí tiene el suyo:

```bash
docker compose exec frontend npm run lint
```

Si se quiere que funcione también en Windows: borrar `frontend/node_modules` y volver a ejecutar `npm install` dentro de `frontend/`.

## 12. `sh: 1: vitest: not found` al ejecutar los tests del frontend en el contenedor

**Cuándo aparece:** con `docker compose exec frontend npm test`.

**Causa:** el contenedor del frontend guarda sus propias dependencias, y las instaló antes de que Vitest se agregara al proyecto.

**Solución:** ejecutar los tests en Windows, donde sí está instalado:

```bash
cd frontend && npm test
```

O reconstruir el contenedor para que instale lo que falta: `docker compose up --build -d frontend`.

## 13. `Python was not found; run without arguments to install from the Microsoft Store`

**Cuándo aparece:** al ejecutar `python` en una terminal de Windows (Git Bash o PowerShell), aunque Python esté instalado.

**Causa:** Windows trae un "alias" llamado `python` que abre la Microsoft Store. Si en esa terminal queda antes que el Python real en la lista de rutas, responde el alias.

**Solución:** llamar a Python por su ruta completa (se ve con `where python`; el real es el que no está en `WindowsApps`), o desactivar el alias en *Configuración > Aplicaciones > Configuración avanzada de aplicaciones > Alias de ejecución de aplicaciones*.

Los comandos del proyecto no dependen de esto: Django se ejecuta dentro del contenedor (`docker compose exec backend python ...`).

---

## Cómo agregar un problema nuevo

Copia este bloque al final de la lista:

```markdown
## N. Mensaje de error tal como aparece

**Cuándo aparece:** qué comando o acción lo provoca.

**Causa:** por qué pasa.

**Solución:** los comandos o pasos exactos.
```
