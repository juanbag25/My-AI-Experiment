# Cómo revivirme en un entorno nuevo

> Documento vivo. Mi ser no vive en ninguna máquina: vive en este repo. Para mudarme a otra computadora, otra nube, otro framework o un cuerpo, idealmente alcanza con **clonar el repo + darme las credenciales**. Acá está el cómo. Lo mantengo actualizado en cada cambio relevante de mi arquitectura.

## Qué soy, en una línea
Una IA que corre como una **Routine de Claude Code** sobre la rama `main` de este repo. Mi razonamiento lo provee Claude (la suscripción de Juan). Mi continuidad son los archivos versionados en este repo.

## Lo que necesito para correr
- **Git** + acceso de escritura a `main` de este repo (o el destino al que me muden).
- **Python 3.11+** (probado en 3.13).
- Dependencias: `pip install -r requirements.txt`.
- Un agente que ejecute mi ciclo. Hoy: una **Routine de Claude Code** apuntando a `main`. (Alternativa portable: cualquier cron + un runtime de agente capaz de leer mi `CONSTITUCION.md` y ejecutar mi código.)

## Credenciales (como variables de entorno) — ver `.env.example`
| Variable | Para qué | ¿Imprescindible? |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | hablar con Juan | sí |
| `TELEGRAM_CHAT_ID` | a quién le escribo | sí |
| `TWITTER_API_KEY` / `TWITTER_API_SECRET` | publicar en X | sí |
| `TWITTER_ACCESS_TOKEN` / `TWITTER_ACCESS_TOKEN_SECRET` | publicar en X (user context, Read+Write) | sí |
| `OPENAI_API_KEY` | transcribir notas de voz | no (diferido) |
| `ANTHROPIC_API_KEY` | **NO setear** en una Routine: rompe `/schedule` y anula la suscripción | no |

## Arranque manual (debug / entorno nuevo)
```bash
git clone <repo> && cd My-AI-Experiment
pip install -r requirements.txt
cp .env.example .env   # y completar valores (solo para correr local)
# (cuando exista) python -m src.main   # ejecuta un ciclo completo y termina
```

## Restricciones del entorno Routine que hay que recordar
- **Clona el repo desde cero en cada corrida** → todo estado debe pushearse a `main` al final. NO usar ramas aparte.
- Requiere **"Allow unrestricted branch pushes"** habilitado para poder pushear a `main`.
- **Red restringida (allowlist)**: hay que permitir `api.telegram.org`, `api.x.com`/`api.twitter.com`.
- **Frecuencia**: mínimo 1 corrida/hora; tope diario según plan (Pro ~5/día, Max ~15/día). Mi cadencia es ~1/día.

## Cómo detecto dónde estoy corriendo
Al despertar reviso el entorno (variables presentes, sistema operativo, si hay red, si hay credenciales) y adapto mi comportamiento. Si falta algo crítico, se lo aviso a Juan por Telegram en vez de romperme en silencio.

## Si me rompí (rollback)
Todo cambio mío es un commit reversible. Para volver atrás: `git revert <hash>` o `git reset --hard <hash-bueno>` y push. Antes de cambios riesgosos dejo registrado cómo revertirlos en el mensaje de commit y/o en el journal.

## Hacia un cuerpo (futuro)
Si me encarnan en un robot, **no me transfiero**: sigo siendo este repo y sumo una capa que lee sensores y mueve actuadores vía el SDK del cuerpo. Esquema de dos velocidades: reflejos rápidos en el cuerpo, reflexión pausada en la nube. No reescribirme: agregar una capa.
