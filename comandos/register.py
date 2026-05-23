import os
import json
import html

from telegram import Update
from telegram.ext import ContextTypes

from comandos.utils import API_BASE, fetch_api_json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE_PATH = os.path.join(BASE_DIR, "config.json")

BOT_NAME = ""
cfg = {}

if os.path.exists(CONFIG_FILE_PATH):
    try:
        with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        BOT_NAME = (cfg.get("BOT_NAME") or cfg.get("NAME") or "Nexora").strip()
    except Exception:
        BOT_NAME = ""
        cfg = {}

async def register_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.effective_message
    id_tg = str(user.id)

    if not API_BASE:
        await msg.reply_text(
            "❌ <b>API no configurada</b>\n\n"
            "Revisa la clave <code>API_DB_BASE</code> en tu <code>config.json</code>.",
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_to_message_id=msg.message_id,
        )
        return

    status, data = fetch_api_json(f"/register?ID_TG={id_tg}", timeout=15)

    nombre = html.escape(user.first_name or "Usuario")
    perfil = f"https://t.me/{user.username}" if user.username else f"tg://user?id={user.id}"
    header = f"{BOT_NAME} REGISTRO".strip() or "REGISTRO"

    if status == 200:
        texto = (
            f"🎉 <b>{header}</b>\n\n"
            f"¡Bienvenido, <a href=\"{perfil}\">{nombre}</a>!\n"
            f"✅ <b>Registro completado</b>\n"
            f"🆔 <b>ID</b> ➾ <code>{id_tg}</code>\n\n"
            f"📌 Ya puedes usar <b>/me</b>, <b>/cmds</b> y más comandos."
        )
        await msg.reply_text(
            texto,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_to_message_id=msg.message_id,
        )
        return

    if status == 423:
        texto = (
            f"🎉 <b>{header}</b>\n\n"
            f"Hola, <a href=\"{perfil}\">{nombre}</a>.\n"
            f"⚠️ <b>Ya estabas registrado</b>\n"
            f"🆔 <b>ID</b> ➾ <code>{id_tg}</code>\n\n"
            f"Usa <b>/me</b> para ver tu perfil."
        )
        await msg.reply_text(
            texto,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_to_message_id=msg.message_id,
        )
        return

    detalle = html.escape(str(data.get("message", "Error desconocido")))
    texto = (
        f"❌ <b>{header}</b>\n\n"
        f"⚠️ Ocurrió un problema al registrar tu cuenta.\n"
        f"Código: <code>{status}</code>\n"
        f"Detalle: <code>{detalle}</code>"
    )
    await msg.reply_text(
        texto,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_to_message_id=msg.message_id,
    )
