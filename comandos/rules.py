import html
import json
import os

from telegram import Update
from telegram.ext import ContextTypes


CONFIG_FILE_PATH = "config.json"
OWNER_USERNAME = "@PeruDoxer"


def _get_bot_name() -> str:
    bot_name = "#NEXORA ⇒"
    if not os.path.exists(CONFIG_FILE_PATH):
        return bot_name
    try:
        with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f) or {}
    except Exception:
        return bot_name

    raw = str(cfg.get("BOT_NAME") or cfg.get("NAME") or "").strip()
    if raw and raw.upper() not in {"SPIDERSYN", "#SPIDERSYN", "#SPIDERSYN ⇒"}:
        return raw.replace("<code>", "").replace("</code>", "").strip()
    return bot_name


async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    bot_name = html.escape(_get_bot_name())

    texto = (
        f"<b>{bot_name} REGLAS DEL GRUPO</b>\n\n"
        f"👑 <b>Dueño oficial:</b> {html.escape(OWNER_USERNAME)}\n\n"
        "🚫 <b>PROHIBIDO CONTENIDO +18</b>\n"
        "No se permite publicar, pedir ni compartir material adulto.\n\n"
        "🚫 <b>PROHIBIDO BÚSQUEDAS -18</b>\n"
        "No se aceptan consultas, solicitudes ni búsquedas relacionadas con menores de edad.\n\n"
        "🚫 <b>PROHIBIDO SPAM</b>\n"
        "Evita mensajes repetidos, flood, publicidad o enlaces no autorizados.\n\n"
        "💳 <b>PROHIBIDO VENTAS NO AUTORIZADAS</b>\n"
        "Solo pueden vender usuarios certificados o admins. Si compras a terceros y te estafan, es tu responsabilidad.\n\n"
        "⭕️ <b>RESPETO AL /STAFF</b>\n"
        "Cualquier falta de respeto al staff puede terminar en sanción o ban.\n\n"
        "⚠️ <b>DNI REPETIDO</b>\n"
        "Si dos personas consultan el mismo DNI, se baneará a ambos sin reclamos.\n\n"
        "📌 <b>Usar el bot implica aceptar estas reglas.</b>"
    )

    await msg.reply_text(
        texto,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_to_message_id=msg.message_id,
    )
