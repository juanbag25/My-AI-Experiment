#!/usr/bin/env python3
"""
check_env.py — Preflight de credenciales / variables de entorno.

Herramienta de SETUP / diagnóstico. NO forma parte del ciclo de vida del
agente (eso vive, a futuro, en src/). Sirve para que Juan verifique, ANTES
de prender la Routine, que las credenciales están bien cargadas y que el
agente puede hablar con Telegram y con Twitter/X.

Qué hace (sin efectos secundarios por defecto):
  - Verifica que estén presentes las 6 variables imprescindibles.
  - Avisa si hay variables que NO deberían estar (ANTHROPIC_API_KEY rompe
    la programación de Routines).
  - Telegram: valida el token (getMe) y, best-effort, que el chat sea
    alcanzable (getChat). No envía mensajes salvo que se lo pidas.
  - Twitter/X: valida las 4 credenciales OAuth 1.0a (get_me). NO publica
    ningún tweet.

Nunca imprime el valor completo de un secreto: siempre lo enmascara.

Uso:
    python scripts/check_env.py
    python scripts/check_env.py --telegram-ping   # además manda un "hola" de prueba

Códigos de salida: 0 = todo OK · 1 = falta algo o algo falló.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

# .env opcional: solo para pruebas locales. En la Routine se usan env vars reales.
try:
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except Exception:
    pass

OK = "✅"    # ✅
NO = "❌"    # ❌
WARN = "⚠️"  # ⚠️
INFO = "•"  # •

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


def _get_json(url: str, timeout: int = 15) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "preflight-check"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


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
    ok = True

    # getMe → ¿el token es válido?
    try:
        data = _get_json(f"{base}/getMe")
        if data.get("ok"):
            u = data["result"]
            print(f"  {OK} Token válido. Bot: @{u.get('username')} (id {u.get('id')})")
        else:
            print(f"  {NO} Telegram rechazó el token: {data.get('description')}")
            ok = False
    except urllib.error.HTTPError as e:
        print(f"  {NO} getMe falló (HTTP {e.code}). ¿Token mal copiado o revocado?")
        ok = False
    except Exception as e:
        print(f"  {NO} No pude contactar api.telegram.org: {e}")
        print(f"     (¿Está permitido api.telegram.org en la allowlist de red?)")
        ok = False

    # getChat → ¿el chat_id es alcanzable? (best-effort, no bloquea)
    if chat_id:
        try:
            data = _get_json(f"{base}/getChat?chat_id={urllib.parse.quote(chat_id)}")
            if data.get("ok"):
                c = data["result"]
                who = c.get("username") or c.get("first_name") or c.get("title") or chat_id
                print(f"  {OK} Chat alcanzable: {who} (id {chat_id})")
            else:
                print(f"  {WARN} No pude resolver el chat_id ({data.get('description')}).")
                print(f"     Asegurate de haberle escrito al bot al menos una vez.")
        except Exception as e:
            print(f"  {WARN} No validé el chat_id ({e}). Quizás puedas enviar igual.")
    else:
        print(f"  {NO} Falta TELEGRAM_CHAT_ID.")
        ok = False

    # Ping opcional (efecto visible: te llega un mensaje)
    if send_ping and token and chat_id:
        try:
            payload = urllib.parse.urlencode(
                {"chat_id": chat_id, "text": f"{OK} Preflight: tu agente puede escribirte por acá."}
            ).encode()
            req = urllib.request.Request(f"{base}/sendMessage", data=payload)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            if data.get("ok"):
                print(f"  {OK} Mensaje de prueba enviado. Miralo en Telegram.")
            else:
                print(f"  {NO} sendMessage falló: {data.get('description')}")
                ok = False
        except Exception as e:
            print(f"  {NO} No pude enviar el mensaje de prueba: {e}")
            ok = False

    return ok


def check_twitter() -> bool:
    section("3) Twitter / X (OAuth 1.0a — sin publicar nada)")
    keys = {
        k: os.environ.get(k, "").strip()
        for k in (
            "TWITTER_API_KEY",
            "TWITTER_API_SECRET",
            "TWITTER_ACCESS_TOKEN",
            "TWITTER_ACCESS_TOKEN_SECRET",
        )
    }
    if not all(keys.values()):
        print(f"  {NO} Faltan credenciales de Twitter; no puedo probar.")
        return False

    try:
        import tweepy  # type: ignore
    except ImportError:
        print(f"  {WARN} tweepy no está instalado. Corré: pip install -r requirements.txt")
        return False

    try:
        client = tweepy.Client(
            consumer_key=keys["TWITTER_API_KEY"],
            consumer_secret=keys["TWITTER_API_SECRET"],
            access_token=keys["TWITTER_ACCESS_TOKEN"],
            access_token_secret=keys["TWITTER_ACCESS_TOKEN_SECRET"],
        )
        me = client.get_me(user_auth=True)
        u = me.data
        print(f"  {OK} Credenciales válidas. Autenticado como @{u.username} ({u.name}, id {u.id})")
        print(f"  {INFO} Permiso de escritura: confirmalo en el portal ('Read and write').")
        return True
    except Exception as e:
        msg = str(e)
        print(f"  {NO} Falló la autenticación con Twitter: {msg}")
        if "401" in msg or "Unauthorized" in msg:
            print(f"     → Suele ser una de las 4 claves mal copiada o tokens viejos. Regenerá y reintentá.")
        if "403" in msg:
            print(f"     → Permisos/acceso. Verificá 'Read and write' y que haya crédito/acceso en el portal.")
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
