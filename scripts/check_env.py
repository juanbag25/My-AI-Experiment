#!/usr/bin/env python3
"""
check_env.py — Preflight de credenciales / variables de entorno.

Herramienta de SETUP / diagnóstico. NO forma parte del ciclo de vida del
agente (eso vive, a futuro, en src/). Sirve para verificar, ANTES de prender
la Routine, que las credenciales están bien cargadas y que el agente puede
hablar con Telegram y con Twitter/X.

Diseño a propósito SIN dependencias externas (solo librería estándar de
Python): así corre aunque todavía no se hayan instalado los requirements y
aunque PyPI no esté en la allowlist de red. El runtime del agente sí usará
tweepy/requests (ver requirements.txt); esto es solo el chequeo de arranque.

Qué hace (sin efectos secundarios por defecto):
  - Verifica que estén presentes las 6 variables imprescindibles.
  - Avisa si hay variables que NO deberían estar (ANTHROPIC_API_KEY rompe
    la programación de Routines).
  - Distingue un BLOQUEO DE RED (allowlist de egress) de un error real de
    credenciales, para no confundir un host bloqueado con un token mal puesto.
  - Telegram: valida el token (getMe) y, best-effort, el chat (getChat).
  - Twitter/X: valida las 4 credenciales OAuth 1.0a firmando un GET /2/users/me.
    NO publica ningún tweet.

Nunca imprime el valor completo de un secreto: siempre lo enmascara.

Uso:
    python scripts/check_env.py
    python scripts/check_env.py --telegram-ping   # además manda un "hola" de prueba

Códigos de salida: 0 = todo OK · 1 = falta algo o algo falló.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

# .env opcional: solo para pruebas locales. En la Routine se usan env vars reales.
try:
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except Exception:
    pass

OK = "✅"
NO = "❌"
WARN = "⚠️"
INFO = "•"

REQUIRED = [
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "TWITTER_API_KEY",
    "TWITTER_API_SECRET",
    "TWITTER_ACCESS_TOKEN",
    "TWITTER_ACCESS_TOKEN_SECRET",
]
OPTIONAL = ["OPENAI_API_KEY"]
FORBIDDEN = ["ANTHROPIC_API_KEY"]  # si está seteada, rompe el scheduling de Routines


def mask(value: str) -> str:
    """Muestra solo las puntas de un secreto, nunca el valor completo."""
    v = (value or "").strip()
    if not v:
        return "(vacío)"
    if len(v) <= 8:
        return "•" * len(v) + f" (len {len(v)})"
    return f"{v[:4]}…{v[-4:]} (len {len(v)})"


def section(title: str) -> None:
    print(f"\n=== {title} ===")


def _http(url: str, *, data: bytes | None = None, headers: dict | None = None, timeout: int = 20):
    """GET/POST simple. Devuelve (status, body_str). No levanta en errores HTTP."""
    h = {"User-Agent": "preflight-check"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=data, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def _blocked(body: str) -> bool:
    """¿El proxy de egress bloqueó el host por allowlist?"""
    b = (body or "").lower()
    return "not in allowlist" in b or "network egress" in b


def check_presence() -> bool:
    section("1) Variables de entorno")
    ok = True
    for name in REQUIRED:
        val = os.environ.get(name, "")
        if val.strip():
            print(f"  {OK} {name} = {mask(val)}")
        else:
            print(f"  {NO} {name} — FALTA")
            ok = False
    for name in OPTIONAL:
        val = os.environ.get(name, "")
        if val.strip():
            print(f"  {INFO} {name} = {mask(val)} (opcional, presente)")
        else:
            print(f"  {INFO} {name} — ausente (opcional, OK)")
    for name in FORBIDDEN:
        if os.environ.get(name, "").strip():
            print(f"  {WARN} {name} ESTÁ seteada → quitala: rompe la programación de Routines")
            ok = False
        else:
            print(f"  {OK} {name} ausente (correcto)")
    return ok


def check_telegram(send_ping: bool) -> bool:
    section("2) Telegram")
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token:
        print(f"  {NO} Sin TELEGRAM_BOT_TOKEN, no puedo probar.")
        return False

    base = f"https://api.telegram.org/bot{token}"

    # getMe → ¿el token es válido?
    try:
        code, body = _http(f"{base}/getMe")
    except Exception as e:
        print(f"  {NO} No pude contactar api.telegram.org: {e}")
        print(f"     → ¿Está permitido api.telegram.org en la allowlist de egress?")
        return False

    if _blocked(body):
        print(f"  {NO} Bloqueado por la allowlist de red.")
        print(f"     → Agregá api.telegram.org a los dominios de egress permitidos del entorno.")
        return False

    try:
        data = json.loads(body)
    except Exception:
        print(f"  {NO} Respuesta inesperada (HTTP {code}): {body[:160]}")
        return False

    if not data.get("ok"):
        print(f"  {NO} Telegram rechazó el token ({data.get('description')}). ¿Mal copiado o revocado?")
        return False

    u = data["result"]
    print(f"  {OK} Token válido. Bot: @{u.get('username')} (id {u.get('id')})")
    ok = True

    # getChat → ¿el chat_id es alcanzable? (best-effort)
    if chat_id:
        _, cbody = _http(f"{base}/getChat?chat_id={urllib.parse.quote(chat_id)}")
        try:
            cdata = json.loads(cbody)
        except Exception:
            cdata = {}
        if cdata.get("ok"):
            c = cdata["result"]
            who = c.get("username") or c.get("first_name") or c.get("title") or chat_id
            print(f"  {OK} Chat alcanzable: {who} (id {chat_id})")
        else:
            print(f"  {WARN} No pude resolver el chat_id ({cdata.get('description')}).")
            print(f"     Asegurate de haberle escrito al bot al menos una vez.")
    else:
        print(f"  {NO} Falta TELEGRAM_CHAT_ID.")
        ok = False

    # Ping opcional (efecto visible: te llega un mensaje)
    if send_ping and chat_id:
        payload = urllib.parse.urlencode(
            {"chat_id": chat_id, "text": f"{OK} Preflight: tu agente puede escribirte por acá."}
        ).encode()
        _, pbody = _http(f"{base}/sendMessage", data=payload)
        try:
            pdata = json.loads(pbody)
        except Exception:
            pdata = {}
        if pdata.get("ok"):
            print(f"  {OK} Mensaje de prueba enviado. Miralo en Telegram.")
        else:
            print(f"  {NO} sendMessage falló: {pdata.get('description') or pbody[:120]}")
            ok = False

    return ok


def _oauth1_header(method: str, url: str, ck: str, cs: str, tok: str, ts: str) -> str:
    """Firma OAuth 1.0a (HMAC-SHA1) para una request sin query params."""
    pe = lambda s: urllib.parse.quote(str(s), safe="")  # RFC3986
    oauth = {
        "oauth_consumer_key": ck,
        "oauth_nonce": uuid.uuid4().hex,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": tok,
        "oauth_version": "1.0",
    }
    param_str = "&".join(f"{pe(k)}={pe(v)}" for k, v in sorted(oauth.items()))
    base_str = "&".join([method.upper(), pe(url), pe(param_str)])
    signing_key = f"{pe(cs)}&{pe(ts)}"
    sig = base64.b64encode(
        hmac.new(signing_key.encode(), base_str.encode(), hashlib.sha1).digest()
    ).decode()
    oauth["oauth_signature"] = sig
    return "OAuth " + ", ".join(f'{pe(k)}="{pe(v)}"' for k, v in sorted(oauth.items()))


def check_twitter() -> bool:
    section("3) Twitter / X (OAuth 1.0a — sin publicar nada)")
    ck = os.environ.get("TWITTER_API_KEY", "").strip()
    cs = os.environ.get("TWITTER_API_SECRET", "").strip()
    tok = os.environ.get("TWITTER_ACCESS_TOKEN", "").strip()
    ts = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET", "").strip()
    if not all([ck, cs, tok, ts]):
        print(f"  {NO} Faltan credenciales de Twitter; no puedo probar.")
        return False

    url = "https://api.x.com/2/users/me"
    try:
        auth = _oauth1_header("GET", url, ck, cs, tok, ts)
        code, body = _http(url, headers={"Authorization": auth})
    except Exception as e:
        print(f"  {NO} No pude contactar api.x.com: {e}")
        print(f"     → ¿Está permitido api.x.com en la allowlist de egress?")
        return False

    if _blocked(body):
        print(f"  {NO} Bloqueado por la allowlist de red.")
        print(f"     → Agregá api.x.com (y api.twitter.com) a los dominios de egress del entorno.")
        return False

    try:
        data = json.loads(body)
    except Exception:
        print(f"  {NO} Respuesta inesperada (HTTP {code}): {body[:160]}")
        return False

    if code == 200 and data.get("data"):
        u = data["data"]
        print(f"  {OK} Credenciales válidas. Autenticado como @{u.get('username')} ({u.get('name')}, id {u.get('id')})")
        print(f"  {INFO} Permiso de escritura: confirmalo en el portal ('Read and write').")
        return True

    detail = data.get("detail") or data.get("title") or (data.get("errors") or [{}])[0].get("message") or body[:160]
    print(f"  {NO} Twitter respondió HTTP {code}: {detail}")
    if code in (401, 403):
        print(f"     → Suele ser una de las 4 claves mal copiada, tokens viejos o permisos. Regenerá y reintentá.")
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description="Preflight de credenciales del agente.")
    ap.add_argument(
        "--telegram-ping",
        action="store_true",
        help="Además, enviar un mensaje de prueba por Telegram (efecto visible).",
    )
    args = ap.parse_args()

    print("Preflight — variables de entorno y conectividad")
    print("(no publica tweets; el ping de Telegram es opt-in)")

    pres_ok = check_presence()
    tg_ok = check_telegram(send_ping=args.telegram_ping)
    tw_ok = check_twitter()

    section("Resumen")
    for ok, label in ((pres_ok, "Variables de entorno"), (tg_ok, "Telegram"), (tw_ok, "Twitter / X")):
        print(f"  {OK if ok else NO} {label}")

    print()
    if pres_ok and tg_ok and tw_ok:
        print(f"{OK} Todo listo. Podés prender la Routine con confianza.")
        return 0
    print(f"{NO} Algo falta o falla. Revisá los puntos en rojo de arriba.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
