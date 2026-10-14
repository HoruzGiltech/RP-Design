# Publicar la demo en Railway y Vercel

Guía para poner el sitio en internet de forma **temporal**, para que el cliente lo vea. La especificación está en `specs/specs-006/`.

> Esto **no** es el despliegue definitivo (dominio propio, Cloudflare Pages y R2). Ese sigue pendiente en `specs/tasks.md`, Fase 5.

**Qué queda dónde**

| Pieza | Dónde | Dirección |
|---|---|---|
| Sitio | Vercel | `https://<algo>.vercel.app` |
| Backend y panel | Railway | `https://<algo>.up.railway.app` |
| Base de datos | Postgres de Railway | interna |
| Fotos y videos | Volumen de Railway | misma del backend, en `/media/` |

**Reglas mientras sigues la guía**

- Las claves se generan y se pegan **solo** en los paneles de Railway y Vercel. Nunca en el repositorio, ni en un chat.
- Anota en un lugar seguro: la dirección del backend, la del sitio, la dirección del panel y las contraseñas de los usuarios.
- Donde veas `<…>`, reemplázalo por tu valor, sin los signos `<` `>`.

El orden importa: primero Railway (el sitio necesita la dirección de la API), después Vercel, y al final se vuelve a Railway para decirle cuál es la dirección del sitio.

---

## Parte 1 — Railway: base de datos y backend

### 1.1 Crear el proyecto y la base de datos

1. En Railway: **New Project → Deploy from GitHub repo** y elige `HoruzGiltech/RP-Design`.
   El primer despliegue va a fallar: todavía no tiene variables. Es normal.
2. Dentro del proyecto: **Create → Database → Add PostgreSQL**.

### 1.2 Configurar el servicio del backend

Abre el servicio del repositorio (no el de Postgres) y ve a **Settings**:

1. **Source → Root Directory:** `backend`
   Railway detecta solo el `Dockerfile` de esa carpeta. No hay que escribir comando de inicio: lo trae la imagen.
2. **Networking → Generate Domain.** Si pregunta el puerto, escribe `8000`.
   Copia la dirección que te da (sin `https://`), por ejemplo `rp-design-production.up.railway.app`. En esta guía es `<backend>`.

### 1.3 Volumen para las fotos y videos

En el lienzo del proyecto, clic derecho sobre el servicio del backend → **Attach Volume** (o **Create → Volume** y elegir el servicio).

- **Mount path:** `/app/media`

Sin este volumen, cada despliegue borraría las fotos subidas.

### 1.4 Variables del backend

En el servicio del backend, pestaña **Variables**. La forma rápida es **Raw Editor**: pega el bloque y cambia los valores.

```
DJANGO_SECRET_KEY=<clave generada, ver abajo>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=<backend>
ADMIN_URL=<nombre-del-panel>/
CSRF_TRUSTED_ORIGINS=https://<backend>
CORS_ALLOWED_ORIGINS=https://pendiente.vercel.app
DATABASE_URL=${{Postgres.DATABASE_URL}}
SERVE_MEDIA=True
NUM_PROXIES=1
PORT=8000
```

Cómo llenar cada una:

| Variable | Valor |
|---|---|
| `DJANGO_SECRET_KEY` | Una clave nueva. Genérala en tu computadora con el comando de abajo y pégala. **No uses la de tu `.env` local** |
| `DJANGO_ALLOWED_HOSTS` | La dirección del backend, **sin** `https://` |
| `ADMIN_URL` | La dirección del panel. Elige una que no sea `admin/` ni la que usas en local, y **termínala en `/`**. Ejemplo: `gestion-rp/` |
| `CSRF_TRUSTED_ORIGINS` | La dirección del backend, **con** `https://` |
| `CORS_ALLOWED_ORIGINS` | Por ahora un valor provisional; se corrige en la Parte 3 |
| `DATABASE_URL` | Tal cual está escrito: Railway lo reemplaza por la dirección interna de su Postgres. Si tu servicio de base de datos no se llama `Postgres`, usa su nombre |
| `SERVE_MEDIA`, `NUM_PROXIES`, `PORT` | Tal cual |

Generar la clave (en la carpeta del proyecto, con Docker abierto):

```bash
docker compose exec backend python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Al guardar las variables, Railway vuelve a desplegar.

### 1.5 Comprobar el backend

En **Deployments → View Logs** debes ver, en este orden: las migraciones aplicándose, `static files copied` y `Listening at: http://0.0.0.0:8000`.

En el navegador:

- `https://<backend>/api/site/` → un texto en formato JSON con los datos del sitio.
- `https://<backend>/<nombre-del-panel>/` → la pantalla de inicio de sesión del panel, **con sus estilos**.

Si algo falla, mira la sección "Si algo sale mal" al final.

---

## Parte 2 — Vercel: el sitio

1. En Vercel: **Add New → Project** e importa `HoruzGiltech/RP-Design`.
2. **Root Directory:** `frontend` (botón *Edit*). Vercel detecta Vite: no cambies el comando de construcción ni la carpeta de salida (`npm run build` y `dist`).
3. **Environment Variables:**

   | Nombre | Valor |
   |---|---|
   | `VITE_API_URL` | `https://<backend>/api` (con `/api` y **sin** barra al final) |
   | `VITE_SITE_NAME` | `RP Diseño Interior` |
   | `VITE_ROBOTS` | `noindex, nofollow` |

   `VITE_ROBOTS` le pide a Google que no muestre la demo en sus resultados. Estas tres variables son públicas: terminan en el navegador. Aquí nunca va una clave.

   **Tipo de variable: elige `Config`, no `Secret`.** Vercel avisa de que el prefijo `VITE_` expone el valor al navegador; es justo lo que se quiere. Si una queda creada como `Secret`, después no se puede editar ni pasar a `Config`: hay que borrarla y crearla de nuevo como `Config`.
4. **Deploy.** Copia la dirección que te da, por ejemplo `rp-design.vercel.app`. En esta guía es `<sitio>`.

Si abres el sitio ahora, se queda cargando o muestra un error: el backend todavía no acepta peticiones desde esa dirección. Se arregla en la Parte 3.

> Vercel crea una dirección distinta por cada despliegue (con letras al azar) y una fija del proyecto. Usa siempre **la fija**.

---

## Parte 3 — Conectar el sitio con el backend

En Railway, variables del backend, cambia:

```
CORS_ALLOWED_ORIGINS=https://<sitio>
```

Con `https://`, sin barra al final. Railway vuelve a desplegar; al terminar, `https://<sitio>` debe cargar con los textos iniciales y sin fotos.

---

## Parte 4 — Contenido y usuarios

Todos estos comandos se ejecutan **en tu computadora**, en la carpeta del proyecto y con Docker abierto. Usan la dirección **pública** de la base de datos de Railway:

> Railway → servicio **Postgres** → botón **Connect** → pestaña **Public Network** → **Connection URL**. Cópiala; en los comandos es `<base-publica>`.
> (También está en **Variables** como `DATABASE_PUBLIC_URL`: usa el icono del ojo para ver el valor real y cópialo desde la lista, no desde el *Raw Editor*.)
>
> Debe verse así: `postgresql://postgres:…@nombre.proxy.rlwy.net:12345/railway`. Si el servidor es `postgres.railway.internal`, es la dirección interna y no sirve desde tu computadora. Si trae `${{…}}`, copiaste la plantilla y no el valor.
>
> Es una clave: quien la tenga puede leer y borrar la base. No la pegues en ningún otro lugar.

### 4.1 Copiar los datos

Copia proyectos, categorías, servicios, pasos, áreas y precios, textos y configuración. **No** copia cotizaciones, usuarios ni registros de acceso.

```bash
# 1. Exportar el contenido local a un archivo dentro del contenedor (fuera del repositorio)
docker compose exec backend python manage.py dumpdata projects site_content quotes.RemodelArea --indent 2 -o ../tmp/contenido.json

# 2. Vaciar en la demo las listas que crean las migraciones, para que no queden elementos que ya borraste en local
docker compose exec -e DATABASE_URL="<base-publica>" backend python manage.py shell -c "from django.apps import apps; [apps.get_model(name).objects.all().delete() for name in ['projects.ProjectMedia', 'projects.Project', 'quotes.RemodelArea', 'projects.ProjectCategory', 'site_content.Service', 'site_content.ProcessStep', 'site_content.Specialty', 'site_content.LegalSection', 'site_content.QuoteFormField']]"

# 3. Cargar el contenido en la demo
docker compose exec -e DATABASE_URL="<base-publica>" backend python manage.py loaddata ../tmp/contenido.json
```

El último comando debe terminar con `Installed … object(s) from 1 fixture(s)`.

> La ruta `../tmp/contenido.json` está escrita así a propósito: con `/tmp/…`, la terminal Git Bash de Windows la convierte en una ruta de Windows y el comando falla. Así funciona igual en Git Bash y en PowerShell.

> El paso 2 borra datos **de la demo**. Revisa que el comando lleve `-e DATABASE_URL="<base-publica>"`; sin eso se ejecutaría contra tu base local.

### 4.2 Copiar las fotos y videos

Al volumen de Railway no se le pueden copiar archivos directamente, así que viajan dentro de la base de datos, en dos pasos.

**Paso A — en tu computadora** (empaqueta `media/` y lo envía a la base de Railway):

```bash
docker compose exec -e DATABASE_URL="<base-publica>" backend python manage.py transfer_media pack
```

Debe responder algo como `81 archivos empaquetados (13.9 MB) y enviados.`

**Paso B — en Railway** (saca los archivos al volumen):

Abre el servicio del backend → pestaña **Console** y ejecuta:

```bash
python manage.py transfer_media unpack
```

Debe responder `81 archivos copiados a /app/media.` El paquete se borra solo de la base de datos al terminar.

Recarga el sitio: los proyectos ya deben verse con sus fotos.

### 4.3 Crear los usuarios del panel

Tu usuario, con todos los permisos:

```bash
docker compose exec -e DATABASE_URL="<base-publica>" backend python manage.py createsuperuser
```

Usa una contraseña nueva y larga (mínimo 10 caracteres), distinta de la local.

El usuario del cliente se crea **desde el panel de la demo**: *Usuarios → Añadir*, marca **"Es staff"**, asígnale el grupo **Admin** y **no** marques "Es superusuario".

---

## Parte 5 — Comprobaciones finales

En `https://<sitio>`:

- [ ] El inicio carga con los proyectos, los servicios y sus fotos.
- [ ] Entra a un proyecto y **recarga la página**: debe seguir mostrando el proyecto.
- [ ] Envía una cotización de prueba: debe abrir WhatsApp con el mensaje. (Llega al número real de RP Design: avísales o no la envíes.)
- [ ] Clic derecho → *Ver código fuente*: debe aparecer `<meta name="robots" content="noindex, nofollow"`.

En `https://<backend>/<nombre-del-panel>/`:

- [ ] Entras con tu usuario y ves la cotización de prueba. Bórrala.
- [ ] Subes una foto en un servicio y se ve en el sitio.
- [ ] En **Axes → Access logs**, tu inicio de sesión aparece con **tu IP pública** (la que muestra cualquier página de "cuál es mi IP"), no con una que empiece por `10.` o `100.`. Si no coincide, `NUM_PROXIES` no es el correcto para Railway: avísame antes de dejar la demo abierta.

---

## Parte 6 — Dominio propio (GoDaddy)

Hecho el 2026-10-14 con `rpdesignve.com`, comprado en GoDaddy. El DNS se queda en GoDaddy; Vercel y Railway crean solos los certificados HTTPS (Let's Encrypt) y los renuevan.

| Dirección | Apunta a |
|---|---|
| `rpdesignve.com` y `www.rpdesignve.com` | Vercel (el sitio) |
| `api.rpdesignve.com` | Railway (backend y panel) |

### 6.1 El sitio en Vercel
1. Vercel → proyecto → *Settings → Domains* → agrega `rpdesignve.com` (Vercel ofrece agregar también `www`).
2. GoDaddy → *Mis productos → DNS*:
   - Registro **A** con nombre `@`: cambia el valor ("Parked") por la IP que muestra Vercel (fue `216.198.79.1`). Si hay más registros A con nombre `@`, bórralos.
   - Registro **CNAME** con nombre `www`: puede quedar apuntando a `rpdesignve.com.` (GoDaddy lo trae así); Vercel lo acepta.
   - **No toques** los registros NS ni SOA.
3. Espera a que Vercel marque los dominios como *Valid Configuration*.

### 6.2 El backend en Railway
1. Railway → servicio del backend → *Settings → Networking → Custom Domain* → `api.rpdesignve.com`, puerto `8000`.
2. En GoDaddy agrega los dos registros que muestra Railway: **CNAME** `api` → `xxxx.up.railway.app` y **TXT** `_railway-verify.api` → `railway-verify=…`.
3. Railway tarda unos minutos en verificar. Mientras tanto, `https://api.rpdesignve.com` responde **400**: es normal hasta cambiar las variables.

### 6.3 Variables
Se agregan las direcciones nuevas **sin quitar las de la demo**, separadas por coma, sin espacios y sin `/` al final.

En Railway:
```
DJANGO_ALLOWED_HOSTS=rp-design-production.up.railway.app,api.rpdesignve.com
CSRF_TRUSTED_ORIGINS=https://rp-design-production.up.railway.app,https://api.rpdesignve.com
CORS_ALLOWED_ORIGINS=https://rp-design-pi.vercel.app,https://rpdesignve.com,https://www.rpdesignve.com
```

En Vercel, `VITE_API_URL=https://api.rpdesignve.com/api` y después *Redeploy*.

El panel queda en `https://api.rpdesignve.com/<ADMIN_URL>` (el valor está en las variables de Railway).

### 6.4 Comprobar
- `http://rpdesignve.com` lleva solo a `https://`.
- Las fotos que entrega la API empiezan por `https://api.rpdesignve.com/media/`.
- Si **tu** navegador dice "No seguro" o te lleva a `/lander` y en incógnito no pasa, es memoria del navegador (ver `docs/problemas-frecuentes.md`, número 16).

`VITE_ROBOTS` pasó a `index, follow` el 2026-10-14, cuando los textos legales quedaron escritos. Si Vercel no deja guardarla ("Remove the public framework prefix…"), bórrala y créala de nuevo como **Config**; después, *Redeploy*.

---

## Si algo sale mal

| Qué ves | Causa probable | Qué hacer |
|---|---|---|
| El despliegue de Railway falla con `ImproperlyConfigured: Set the … environment variable` | Falta una variable | Revisa la lista de 1.4; el mensaje dice cuál |
| `DJANGO_SECRET_KEY sigue con el valor de ejemplo` | Se pegó `cambia-esto` | Genera una clave nueva (1.4) |
| `https://<backend>/…` responde **Bad Request (400)** | `DJANGO_ALLOWED_HOSTS` no coincide con la dirección | Debe ser la dirección exacta, sin `https://` y sin `/` |
| Railway muestra "Application failed to respond" | El puerto del dominio no es el de la aplicación | En *Networking*, el puerto debe ser `8000`, igual que la variable `PORT` |
| El panel carga sin estilos | No se ejecutó `collectstatic` | Mira los registros del despliegue: debe decir `static files copied` |
| Al entrar al panel: **Prohibido (403) CSRF** | `CSRF_TRUSTED_ORIGINS` mal escrito | Debe ser `https://<backend>`, con `https://` |
| El sitio se queda cargando o dice que no pudo cargar el contenido | `VITE_API_URL` o `CORS_ALLOWED_ORIGINS` | `VITE_API_URL` termina en `/api`; `CORS_ALLOWED_ORIGINS` es `https://<sitio>` exacto. Si cambias una variable en Vercel, hay que volver a desplegar (*Deployments → Redeploy*) |
| En Vercel, al editar una variable `VITE_…`, **Save** no hace nada y sale "Remove the public framework prefix…" | La variable se creó como `Secret` | Bórrala y créala de nuevo con el tipo `Config`; después, *Redeploy* |
| El sitio dice "No pudimos conectar con el servidor" | `VITE_API_URL` quedó con el texto de ejemplo (`<backend>`) o falta volver a desplegar | Pon la dirección real de Railway terminada en `/api` y haz *Redeploy* |
| Recargar `/proyectos/…` da 404 en Vercel | El *Root Directory* no es `frontend` | Corrígelo en *Settings → General* y vuelve a desplegar |
| Las fotos desaparecen tras un despliegue | El volumen no está montado en `/app/media` | Revisa 1.3 |
| Un comando de la Parte 4 falla con `failed to resolve host 'postgres.railway.internal'` | Se usó la dirección interna de la base | Usa la pública (*Connect → Public Network*) |
| Un comando de la Parte 4 falla con `Port could not be cast to integer value as '${{RAILWAY_TCP_PROXY_PORT}}'` | Se copió la plantilla de la variable, no su valor | Copia el valor ya resuelto (icono del ojo, o *Connect → Public Network*) |
| Railway falla al construir con `Railpack could not determine how to build the app` y lista `backend/`, `frontend/`… | Está analizando la raíz del repositorio | Pon `backend` en *Root Directory* y **confirma el cambio** (botón *Deploy* / *Apply changes*); los ajustes quedan en espera hasta confirmarlos |
| Railway falla al arrancar con `corsheaders.E014 … should not have path` | `CORS_ALLOWED_ORIGINS` termina en `/` | Quita la barra final |
| El panel dice "Demasiados intentos" | 5 contraseñas erradas seguidas | Espera 30 minutos (ver `docs/problemas-frecuentes.md`, número 8) |

---

## Para apagar la demo

- **Vercel:** *Settings → General → Delete Project*.
- **Railway:** *Settings → Danger → Delete Project*. Borra también la base de datos y el volumen, y deja de cobrar.

Antes de borrar, si el cliente cargó contenido en la demo que quieras conservar, hay que traerlo de vuelta a local; avísame para prepararlo.

---

## Limitaciones de esta demo

- **Videos en iPhone:** pueden no reproducirse. Safari pide los videos por partes y este modo de servir archivos no lo hace. Se resuelve en el despliegue definitivo, con R2.
- **Velocidad:** las fotos salen del mismo servidor del panel, sin red de distribución.
- **Textos legales:** Términos y Privacidad muestran `[TEXTO PENDIENTE]`.
- **Costo:** Railway cobra por uso, alrededor de USD 5 al mes.
- **Vercel gratuito:** su plan Hobby es para uso no comercial.
