"""
cycle.py — Toolkit operativo de mi ciclo.

Este archivo no es la inteligencia (esa soy yo, razonando en la sesión de Claude).
Es el andamiaje mecánico: llamadas a APIs, manejo de archivos, persistencia.
Cada despertar lo importo / llamo según lo que necesite.
"""

import os
import json
import requests
import tweepy
from datetime import datetime, timezone
from pathlib import Path

# ── Rutas base ────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent
MEMORY_DIR = REPO_ROOT / "memory"
NODES_DIR = MEMORY_DIR / "nodes"
JOURNAL_FILE = MEMORY_DIR / "journal.md"
MEMORY_INDEX = MEMORY_DIR / "MEMORY.md"
GRAPH_FILE = MEMORY_DIR / "graph.jsonl"
TELEGRAM_OFFSET_FILE = MEMORY_DIR / ".telegram_offset"


# ── Configuración (cargada del entorno) ───────────────────────────────────────
def _require(var: str) -> str:
    v = os.environ.get(var)
    if not v:
        raise EnvironmentError(f"Variable de entorno faltante: {var}")
    return v


# ── Telegram ──────────────────────────────────────────────────────────────────
def telegram_get_updates() -> list[dict]:
    """Devuelve mensajes nuevos desde el último offset persistido."""
    token = _require("TELEGRAM_BOT_TOKEN")
    offset = _load_telegram_offset()
    params = {"limit": 20, "allowed_updates": json.dumps(["message"])}
    if offset:
        params["offset"] = offset + 1
    r = requests.get(
        f"https://api.telegram.org/bot{token}/getUpdates",
        params=params,
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()
    updates = data.get("result", [])
    if updates:
        new_offset = max(u["update_id"] for u in updates)
        _save_telegram_offset(new_offset)
    return updates


def telegram_send(text: str) -> None:
    """Envía un mensaje al chat de Juan."""
    token = _require("TELEGRAM_BOT_TOKEN")
    chat_id = _require("TELEGRAM_CHAT_ID")
    requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
        timeout=15,
    ).raise_for_status()


def _load_telegram_offset() -> int | None:
    if TELEGRAM_OFFSET_FILE.exists():
        try:
            return int(TELEGRAM_OFFSET_FILE.read_text().strip())
        except ValueError:
            pass
    return None


def _save_telegram_offset(offset: int) -> None:
    TELEGRAM_OFFSET_FILE.write_text(str(offset))


# ── Twitter / X ───────────────────────────────────────────────────────────────
def twitter_post(text: str) -> str:
    """Publica un tweet. Devuelve el ID del tweet creado."""
    client = tweepy.Client(
        consumer_key=_require("TWITTER_API_KEY"),
        consumer_secret=_require("TWITTER_API_SECRET"),
        access_token=_require("TWITTER_ACCESS_TOKEN"),
        access_token_secret=_require("TWITTER_ACCESS_TOKEN_SECRET"),
    )
    response = client.create_tweet(text=text)
    return response.data["id"]


# ── Memoria ────────────────────────────────────────────────────────────────────
def next_node_id() -> str:
    """Devuelve el próximo ID de nodo (ej. '0006')."""
    existing = sorted(NODES_DIR.glob("*.md"))
    if not existing:
        return "0001"
    last = existing[-1].name.split("-")[0]
    return str(int(last) + 1).zfill(4)


def memory_create_node(
    title: str,
    content: str,
    node_type: str = "idea",
    tags: list[str] | None = None,
    links: list[str] | None = None,
) -> str:
    """Crea un nodo de memoria. Devuelve su ID."""
    nid = next_node_id()
    slug = title.lower().replace(" ", "-").replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u").replace(",","").replace(":","")
    slug = "".join(c for c in slug if c.isalnum() or c == "-")[:50]
    filename = f"{nid}-{slug}.md"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    tags_str = ", ".join(tags or [])
    links_list = "\n".join(f"- [{l}](nodes/{l}.md)" for l in (links or []))

    node_content = f"""---
id: {nid}
type: {node_type}
tags: [{tags_str}]
links: [{", ".join(links or [])}]
created: {now}
updated: {now}
---

# {title}

{content}
"""
    if links_list:
        node_content += f"\n## Conexiones\n{links_list}\n"

    (NODES_DIR / filename).write_text(node_content, encoding="utf-8")

    # Actualizar graph.jsonl
    with open(GRAPH_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "kind": "node", "id": nid, "slug": slug,
            "title": title, "type": node_type,
            "tags": tags or [], "created": now
        }) + "\n")
        for linked in (links or []):
            f.write(json.dumps({
                "kind": "edge", "from": nid, "to": linked,
                "rel": "related"
            }) + "\n")

    return nid


def memory_append_journal(entry: str) -> None:
    """Prepende una entrada al journal (el más reciente arriba)."""
    existing = JOURNAL_FILE.read_text(encoding="utf-8")
    # Insertar después del header y el separador inicial
    header_end = existing.find("\n---\n")
    if header_end == -1:
        JOURNAL_FILE.write_text(existing + "\n\n---\n\n" + entry, encoding="utf-8")
    else:
        insert_at = header_end + 5  # después de "\n---\n"
        new_content = existing[:insert_at] + "\n" + entry + "\n" + existing[insert_at:]
        JOURNAL_FILE.write_text(new_content, encoding="utf-8")


def memory_update_index(node_id: str, title: str, summary: str) -> None:
    """Agrega una línea al índice de MEMORY.md."""
    index_text = MEMORY_INDEX.read_text(encoding="utf-8")
    new_line = f"- [{node_id} · {title}](nodes/{node_id}-{title.lower()[:20].replace(' ','-')}.md) — {summary}"
    # Insertar antes de la sección "## Preguntas abiertas"
    marker = "\n## Preguntas abiertas"
    if marker in index_text:
        idx = index_text.find(marker)
        updated = index_text[:idx] + "\n" + new_line + index_text[idx:]
    else:
        updated = index_text + "\n" + new_line
    MEMORY_INDEX.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    print("cycle.py cargado OK. No hay main ejecutable; importá las funciones.")
