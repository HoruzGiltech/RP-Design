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

---

## Cómo agregar un problema nuevo

Copia este bloque al final de la lista:

```markdown
## N. Mensaje de error tal como aparece

**Cuándo aparece:** qué comando o acción lo provoca.

**Causa:** por qué pasa.

**Solución:** los comandos o pasos exactos.
```
