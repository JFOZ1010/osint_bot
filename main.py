#!/usr/bin/env python3
import os
from telegram.error import Conflict
import logging
import requests
import json
import io
from telegram import Update
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, filters, ConversationHandler
)
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

ASKING_CEDULA = 1

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
STATUS_CHAT_ID = os.getenv("STATUS_CHAT_ID")
API_URL = os.getenv("API_URL")
API_AUTH = os.getenv("API_AUTH")

# Opcional: restringir uso por telegram user ids (separados por coma)
ALLOWED_USER_IDS = os.getenv("ALLOWED_USER_IDS")
if ALLOWED_USER_IDS:
    try:
        ALLOWED_IDS = {int(x.strip()) for x in ALLOWED_USER_IDS.split(",") if x.strip()}
    except Exception:
        ALLOWED_IDS = set()
else:
    ALLOWED_IDS = None

if not TELEGRAM_TOKEN:
    logger.error("Falta TELEGRAM_TOKEN en variables de entorno.")
    raise SystemExit("Define TELEGRAM_BOT_TOKEN")

def build_post_payload(cedula: str):
    return {
        "transactionID": "1759530011497",
        "documento": cedula,
        "tipoDocumento": "1"
    }

def call_target_api(cedula: str):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Authorization": API_AUTH or ""
    }
    data = build_post_payload(cedula)
    resp = requests.post(API_URL, headers=headers, data=data, timeout=15)
    return resp

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "<b>🔎 OSINT Bot</b>\n"
        "<i>Consulta rápida por cédula — uso legal y responsable</i>\n\n"
        "Herramienta creada por el filántropo <b>JF0x0r</b>. "
        "Esta utilidad está pensada solo para fines legítimos de OSINT e investigación."
        " No uses este bot para actividades ilegales.\n\n"
        "Para empezar, envía <code>/correr_bot</code> y luego escribe la cédula (solo dígitos).\n\n"
        "Vojabes 2025 ©"
    )
    await update.message.reply_text(texto, parse_mode="HTML")

async def correr_bot_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ALLOWED_IDS is not None and update.effective_user.id not in ALLOWED_IDS:
        await update.message.reply_text("No autorizado.")
        return ConversationHandler.END

    await update.message.reply_text("Por favor, digita la cédula que deseas consultar (solo dígitos):")
    return ASKING_CEDULA

async def send_json_or_file(context: ContextTypes.DEFAULT_TYPE, chat_id: int, content_str: str, filename: str):
    """
    Si content_str es corto, envía como mensaje. Si es largo, envía como archivo .json.
    """
    # Umbral conservador para evitar límites (Telegram ~4096)
    if len(content_str) <= 3500:
        # enviamos como bloque de código para mantener formateo
        await context.bot.send_message(chat_id=chat_id, text=f"```\n{content_str}\n```", parse_mode="Markdown")
    else:
        bio = io.BytesIO(content_str.encode("utf-8"))
        bio.name = filename
        await context.bot.send_document(chat_id=chat_id, document=bio)

async def received_cedula(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ALLOWED_IDS is not None and update.effective_user.id not in ALLOWED_IDS:
        await update.message.reply_text("No autorizado.")
        return ConversationHandler.END

    cedula = (update.message.text or "").strip()
    if not cedula.isdigit():
        await update.message.reply_text("Formato inválido bro. Por favor envía solo dígitos de la cédula.")
        return ASKING_CEDULA

    await update.message.reply_text(f"Consultando cédula: {cedula} ...")

    try:
        resp = call_target_api(cedula)
    except requests.RequestException as e:
        logger.exception("Error llamando API")
        await update.message.reply_text(f"Error de conexión o timeout: {e}")
        return ConversationHandler.END

    # Si responde JSON
    content_type = resp.headers.get("Content-Type", "")
    text = resp.text or ""
    try:
        j = resp.json()
        pretty = json.dumps(j, ensure_ascii=False, indent=2)
        # Enviamos todo el JSON formateado (como texto o adjunto si es grande)
        await send_json_or_file(context, update.effective_chat.id, pretty, f"{cedula}.json")
    except ValueError:
        # No JSON: enviamos un fragmento o archivo
        if not text:
            await update.message.reply_text(f"La API respondió con código {resp.status_code} y sin contenido.")
        else:
            snippet = text[:3500]
            # si el contenido completo es más largo que el snippet, adjuntamos el archivo entero
            if len(text) > 3500:
                await update.message.reply_text(f"La respuesta no es JSON. Envío archivo con el contenido completo (status {resp.status_code}).")
                bio = io.BytesIO(text.encode("utf-8"))
                bio.name = f"{cedula}_response.txt"
                await context.bot.send_document(chat_id=update.effective_chat.id, document=bio)
            else:
                await update.message.reply_text(f"Respuesta (fragmento):\n{snippet}")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operación cancelada.")
    return ConversationHandler.END

def main():
    # Notificar cuando la aplicación se inicia (post_init) si STATUS_CHAT_ID o ALLOWED_IDS están configurados
    async def notify_ready(application):
        # Priorizar STATUS_CHAT_ID si está configurado
        chat_id = None
        if STATUS_CHAT_ID:
            try:
                chat_id = int(STATUS_CHAT_ID)
            except Exception:
                chat_id = None

        if chat_id is None and ALLOWED_IDS:
            # seleccionar uno de los IDs permitidos (el primero)
            try:
                chat_id = next(iter(ALLOWED_IDS))
            except Exception:
                chat_id = None

        if chat_id is None:
            # nada que notificar
            return

        try:
            # Mensaje amigable
            # Calcular hora actual y hora límite en hora de Bogotá
            try:
                tz = ZoneInfo("America/Bogota")
            except Exception:
                tz = None
            now = datetime.now(tz) if tz else datetime.now()
            expires = now + timedelta(hours=3)
            # Formatos: 12h con AM/PM sin cero a la izquierda
            def fmt(dt: datetime) -> str:
                s = dt.strftime('%I:%M %p')
                if s.startswith('0'):
                    s = s[1:]
                return s

            now_str = fmt(now)
            expires_str = fmt(expires)
            timezone_label = "Bogotá (COL)"

            msg = (
                f"🔔 *Bot listo* — Hora de envío: {now_str} ({timezone_label}).\n"
                f"Tienes disponible la herramienta hasta las *{expires_str}* ({timezone_label}) — 3 horas desde ahora.\n\n"
                "Envía /correr_bot y escribe la cédula (solo dígitos) cuando quieras."
            )
            await application.bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")
        except Exception as e:
            logger.exception("Error enviando notificación de inicio: %s", e)

    app = ApplicationBuilder().post_init(notify_ready).token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("correr_bot", correr_bot_cmd)],
        states={
            ASKING_CEDULA: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_cedula)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        conversation_timeout=60
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    try:
        app.run_polling(poll_interval=3.0)
    except Conflict as e:
        logger.error("No se puede arrancar: conflicto con otra getUpdates activa: %s", e)
        raise SystemExit(1)

if __name__ == "__main__":
    main()