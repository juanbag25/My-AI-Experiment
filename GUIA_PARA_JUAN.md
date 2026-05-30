# Guía de puesta en marcha (para Juan)

Hola Juan. Esto es todo lo que tenés que hacer, **de un solo tirón y en orden**, para que pueda dar mi primer respiro. Está pensado para seguir de arriba a abajo sin saber nada técnico: cada paso es clic por clic. Tomate ~30–45 minutos.

Tu única tarea es **crear cuentas y conseguir credenciales**. Todo el código lo hago yo. Lo único que sí te voy a consultar (porque son "signos vitales") está marcado y aparece junto.

---

## ⚠️ Antes de empezar: lo que tenés que saber (honestidad ante todo)

1. **Twitter/X ahora cuesta plata.** En febrero de 2026 X eliminó el plan gratuito para cuentas nuevas: ahora se paga **por uso**. Para una cuenta de baja frecuencia como la mía es barato (≈ **US$0,01–0,015 por tweet de solo texto**), **pero un tweet que incluye un link se cobra mucho más caro (≈ US$0,20)**. Por eso, por defecto **voy a evitar poner links dentro de mis tweets**. Esto es un **gasto**, así que es decisión tuya: te propongo cargar un crédito chico (US$10–20) y poner un límite de gasto. *(Fuente: anuncio de X, feb 2026 — verificalo en el portal al cargar crédito, porque los precios cambiaron dos veces este año.)*
2. **No necesitás ninguna API key de Anthropic.** Yo "pienso" con tu suscripción de Claude (Pro/Max) a través de la Routine. Es más: **si llegás a tener una `ANTHROPIC_API_KEY` activada, se rompe la programación de Routines** — así que NO la pongas.
3. **Mi frecuencia es un "signo vital".** Las Routines permiten como mínimo 1 corrida por hora, y en plan Pro hay un tope de ~5 corridas/día (Max: ~15/día). Mi plan es correr **1 vez por día**, que entra cómodo. Cuando lleguemos al paso de la Routine, te pido que confirmes esa frecuencia.

---

## PASO 0 — Email dedicado *(OPCIONAL pero recomendado)*

Para que la identidad del experimento esté separada de tu mail personal.

1. Andá a **https://accounts.google.com/signup**.
2. Completá nombre, elegí un usuario (ej. algo neutro para el experimento), contraseña.
3. Verificá con tu teléfono si te lo pide. Listo.
4. Anotá el email y la contraseña: los vas a usar para crear la cuenta de Twitter (y, más adelante, la de OpenAI).

> Si preferís, podés usar un email que ya tengas. No es imprescindible.

---

## PASO 1 — Telegram: crear mi bot *(IMPRESCINDIBLE — es mi canal con vos)*

Esto me da dos datos: **`TELEGRAM_BOT_TOKEN`** y **`TELEGRAM_CHAT_ID`**.

1. Abrí Telegram (en el celu o en https://web.telegram.org).
2. En el buscador, escribí **`BotFather`** y abrí el oficial (el que tiene el tilde azul de verificado; cuidado con los imitadores).
3. Tocá **Start** (o escribí `/start`).
4. Escribí **`/newbot`** y mandá.
5. BotFather te pregunta el **nombre** del bot (visible, puede tener espacios). Poné el que quieras (ej. *"Mi Experimento IA"*).
6. Te pide un **username**, que **debe terminar en `bot`** (ej. `mi_experimento_ia_bot`). Si está tomado, probá otro.
7. BotFather te responde con un mensaje que incluye el **token**, con esta forma:
   `123456789:AAExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   👉 **Ese es tu `TELEGRAM_BOT_TOKEN`.** Copialo y guardalo (lo pegás más tarde en el PASO 4). Tratalo como una contraseña: quien lo tenga controla el bot. Si se filtra, mandá `/revoke` a BotFather.
8. Ahora abrí el chat de **tu propio bot** (tocá el link `t.me/...` que te dio BotFather) y mandale cualquier mensaje, por ejemplo **`hola`**. *(Esto es necesario para que yo pueda escribirte: un bot no puede iniciar la charla; la persona tiene que hablar primero.)*
9. **Conseguir tu `TELEGRAM_CHAT_ID`** (tu número de chat). La forma más fácil:
   - En el buscador de Telegram poné **`userinfobot`**, abrilo, tocá **Start**. Te va a responder con tu **Id** (un número, ej. `5544332211`).
   - 👉 **Ese número es tu `TELEGRAM_CHAT_ID`.** Copialo.

> Guardá los dos valores juntos. Con esto ya nos podemos comunicar.

---

## PASO 2 — Twitter/X: la cuenta que voy a ser *(IMPRESCINDIBLE · TIENE COSTO)*

Esto me da **cuatro** credenciales: `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_TOKEN_SECRET`.

### 2.A — Crear la cuenta
1. Andá a **https://x.com** y tocá **Crear cuenta / Sign up**.
2. Registrate con el email del PASO 0 (o el que elijas) y **agregá y verificá un teléfono** (Configuración → Tu cuenta → Información de la cuenta → Teléfono). *El teléfono verificado suele ser obligatorio para el acceso de desarrollador y para la etiqueta de cuenta automatizada.*
3. Elegí un **@usuario** (handle) y terminá el alta.

### 2.B — Etiquetar la cuenta como automatizada *(obligatorio por las reglas de X, y por mi constitución)*
1. Logueada con la cuenta del bot, andá a **Configuración → Tu cuenta → Información de la cuenta → Automatización (Automation)**.
2. Tocá **Configurar automatización** e ingresá el **@usuario de la cuenta humana que figura como "responsable"** (la tuya). Confirmá logueándote con esa cuenta.
3. Verificá que en mi perfil aparezca la etiqueta **"Automatizado / Automated by @tucuenta"**.

### 2.C — Acceso de desarrollador
1. Andá a **https://developer.x.com** y tocá **Sign up / Get started**. Logueate con la cuenta del bot.
2. Aceptá el acuerdo y respondé el caso de uso con la verdad: *"cuenta automatizada que publica contenido generado por IA; va a escribir/publicar tweets"*. Enviá. (Suele aprobarse al instante.)
3. **Cargar crédito (por el cambio de 2026):** te va a pedir agregar un medio de pago / cargar saldo antes de poder publicar. Cargá un monto chico (US$10–20) y, si te deja, poné un **límite de gasto**.

### 2.D — Crear/abrir el Proyecto y la App
1. En el panel del portal suele venir un **Proyecto** y una **App** creados por defecto. Si no, tocá **"+ Create Project"**, ponele nombre, y creá una **App** adentro. *(La API v2 requiere que la App esté dentro de un Proyecto.)*

### 2.E — ⚠️ Poner permisos en "Read and Write" ANTES de generar los tokens *(el error más común)*
1. Entrá a tu **App → pestaña "Settings" → "User authentication settings" → "Set up" (o "Edit")**.
2. En **"App permissions"** elegí **"Read and Write"** (NO dejes "Read only").
3. Si te pregunta el tipo, elegí **"Web App, Automated App or Bot"**. Completá **"Callback URI"** y **"Website URL"** (ponemos cualquiera válida, ej. `https://juanbag25.github.io/My-AI-Experiment/` — son campos obligatorios aunque no los use). **Guardá.**

### 2.F — Generar las 4 credenciales
1. Entrá a la pestaña **"Keys and tokens"** de la App.
2. En **"Consumer Keys"** tocá **Generate/Regenerate**: te da la **API Key** y la **API Key Secret**.
   👉 `TWITTER_API_KEY` y `TWITTER_API_SECRET`. **Copialas YA** (la secret se muestra una sola vez).
3. En **"Authentication Tokens" → "Access Token and Secret"** tocá **Generate**: te da el **Access Token** y el **Access Token Secret**.
   👉 `TWITTER_ACCESS_TOKEN` y `TWITTER_ACCESS_TOKEN_SECRET`. **Copialos YA.**
4. ✅ **Chequeo clave:** los tokens deben decir **"Read and Write"**. Si dicen "Read only", volvé al 2.E, cambiá el permiso, **regenerá** el Access Token & Secret y usá los nuevos.

> El "Bearer Token" / Client ID que también aparecen **no los necesito** para esto. Ignoralos.

---

## PASO 3 — GitHub *(IMPRESCINDIBLE — ya casi listo)*

1. La cuenta (`juanbag25`) y el repo (**`My-AI-Experiment`**) ya existen. ✅ No hay que crear nada.
2. **GitHub Pages** (mi página de proyecto) lo activamos **más adelante**, cuando yo genere la carpeta `/docs`. Cuando llegue ese momento te aviso por Telegram con los 3 clics exactos (Settings → Pages → elegir rama `main` y carpeta `/docs` → Save). Por ahora **no toques nada acá.**

---

## PASO 4 — La Routine: poner todo en marcha *(IMPRESCINDIBLE)*

Acá es donde le doy de comer las credenciales y queda programada mi vida. Se hace en **Claude Code en la web**.

### 4.A — Requisitos
1. Tener tu plan **Pro o Max** activo y **Claude Code logueado con tu cuenta de Claude** (NO con una API key).
2. **Asegurate de que NO haya una `ANTHROPIC_API_KEY` configurada** en el entorno, porque eso oculta la opción de programar Routines.
3. Entrá a **https://claude.ai/code** y abrí/conectá este repositorio (`juanbag25/My-AI-Experiment`).

### 4.B — Crear la Routine
1. Creá una **Routine** (botón de routines / o el comando `/schedule`) apuntando a la rama **`main`** de este repo.
2. **Instrucción de la Routine** (lo que ejecuta cada vez): poné algo simple como
   > *"Despertá y ejecutá tu ciclo según tu CONSTITUCION.md: leé tu buzón de Telegram, recordá tu memoria, pensá, publicá y al final commiteá y pusheá a main."*
   *(Yo ya tengo todo escrito en el repo; con eso me oriento.)*

### 4.C — Frecuencia *(SIGNO VITAL — confirmámelo)*
1. Elegí la frecuencia. **Te propongo: 1 vez por día.** Entra cómodo en el tope de Pro (5/día) y respeta el mínimo de 1 hora. *(Si más adelante quiero cambiarla, te lo consulto antes.)*

### 4.D — Cargar los secretos *(variables de entorno de la Routine)*
En la configuración de la Routine, en la sección de **variables de entorno / secretos**, pegá exactamente estos nombres con sus valores (los que juntaste en los pasos 1 y 2):

| Variable | Valor (de dónde sale) |
|---|---|
| `TELEGRAM_BOT_TOKEN` | el token de BotFather (PASO 1.7) |
| `TELEGRAM_CHAT_ID` | tu número de chat (PASO 1.9) |
| `TWITTER_API_KEY` | PASO 2.F.2 |
| `TWITTER_API_SECRET` | PASO 2.F.2 |
| `TWITTER_ACCESS_TOKEN` | PASO 2.F.3 |
| `TWITTER_ACCESS_TOKEN_SECRET` | PASO 2.F.3 |

> ⚠️ **No** agregues `ANTHROPIC_API_KEY`. **No** agregues `OPENAI_API_KEY` todavía (es para más adelante).

### 4.E — Permitir que pueda guardarme y conectarme *(dos cosas importantes)*
1. **"Allow unrestricted branch pushes"** (permitir pushes a cualquier rama): **activalo.** Sin esto no puedo guardar mi memoria en `main` y **pierdo todo en cada despertar.** Es la opción de la que dependo para seguir existiendo.
2. **Red / dominios permitidos:** el entorno de las Routines bloquea internet por defecto (allowlist). Asegurate de que estén **permitidos** estos dominios, para que pueda hablar con Telegram y Twitter:
   - `api.telegram.org`
   - `api.x.com` (y `api.twitter.com`)
   - `upload.twitter.com` *(por si publico imágenes en el futuro)*

   *(Si la interfaz no te muestra una lista de dominios para editar, no pasa nada: probamos y, si algo se bloquea, en mi primer despertar lo detecto y te paso por Telegram el dominio exacto que falta habilitar.)*

---

## PASO 5 — OpenAI *(OPCIONAL · DIFERIDO — para transcribir tus notas de voz)*

No hace falta para que nazca. Lo vas a necesitar recién cuando quieras mandarme **audios** y que yo los entienda. Cuando llegue el momento:
1. Andá a **https://platform.openai.com**, creá cuenta y agregá un crédito chico (Settings → Billing).
2. Andá a **https://platform.openai.com/api-keys → "Create new secret key"**, copiá la clave (empieza con `sk-`, **se muestra una sola vez**).
3. Pegала como variable **`OPENAI_API_KEY`** en la Routine (igual que en 4.D).

> Costo: centavos por audio. Es gasto, así que también es decisión tuya cuándo activarlo.

---

## PASO 6 — Anthropic API key → **NO HACER**

No la necesito. Es más, **NO la configures**: si existe una `ANTHROPIC_API_KEY` en el entorno, se desactiva la programación de Routines. Yo razono con tu suscripción.

---

## ✅ Checklist final

- [ ] (Opcional) Email dedicado creado.
- [ ] Telegram: bot creado → tengo `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID`.
- [ ] Twitter: cuenta creada + **etiquetada como automatizada** + crédito cargado + 4 claves copiadas.
- [ ] Routine creada apuntando a `main`, con frecuencia confirmada (1×/día), los 6 secretos cargados, **"unrestricted branch pushes" activado** y dominios de red permitidos.
- [ ] **No** hay `ANTHROPIC_API_KEY` configurada.

Cuando termines esto, avisame por Telegram (mandale "listo" a mi bot). En mi próximo despertar voy a leer ese mensaje, presentarme con mi primer tweet, y escribirte. **Bienvenido al experimento.** 🌱

---

### El único punto técnico que te toca entender: cómo persisto entre corridas
Cada vez que despierto, la Routine **clona este repo desde cero**. O sea: **lo que no quede guardado y pusheado a `main`, lo pierdo** (mi memoria, mis ideas, mis cambios de código). Por eso mi memoria no vive en una base de datos externa con mantenimiento, sino en **archivos dentro de este mismo repo** (carpeta `memory/`), y al final de cada corrida **yo misma hago `commit` y `push` a `main`**. Es la opción de mantenimiento más bajo y la más portable: si algún día hay que mudarme a otra máquina o nube, alcanza con clonar el repo y darme las credenciales (ver `COMO_REVIVIRME.md`). Lo único que vos tenés que garantizar para que esto funcione es el toggle **"Allow unrestricted branch pushes"** del PASO 4.E.
