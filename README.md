# OSINT Bot

🔎 Bot ligero para consultas OSINT por identificación (cédula)

Un cliente Telegram pequeño y eficiente que consulta mediante una API `SURPUiA7KQo=` externa, por número de identificación y devuelve datos en formato JSON o como archivo adjunto. Está pensado para uso legal, auditoría y análisis con permisos válidos.

---

## Que carajos escuché mientras hacía esto: 
Mientras automatizas, suena con ritmo:
- "Mucho corazón" — Benny Moré (Año: 1952) 🎺
- "Las cuarenta" — Daniel Santos (Año: 2006) 🎶
- "Mil Cosas" — Alberto Beltrán (Año: 1955)

---

## ¿Qué hace este proyecto?
- Ejecuta consultas contra un endpoint remoto con una cédula (documento).
- Presenta la respuesta de forma legible (texto o adjunto JSON si es largo).
- Soporta ejecuciones en polling (desarrollo / GH Actions) y webhook (servidores con HTTPS).
- Control de acceso opcional por Telegram user IDs.

---

## Características clave
- Compacto, sin dependencias innecesarias.
- Compatible con `python-telegram-bot` v20 y modo `webhook` o `polling`.
- Buenas prácticas: manejo de errores, timeouts y respuesta en texto/archivo.
- Integración CI/CD con GitHub Actions para ejecutar por bloques or manualmente.

---

## Requisitos
- Python 3.11+ (recomendado)
- Un Token de Bot de Telegram (BotFather)
- (Opcional) `WEBHOOK_URL` si decides usar webhook

---

## Instalación local
```bash
git clone https://github.com/JFOZ1010/osint_bot.git
cd osint_bot
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
touch .env  # editar con tus secretos
```

---

## Variables de entorno
Usa un archivo `.env` o variables de entorno en tu host:
- `TELEGRAM_TOKEN` (requerido)
- `API_URL` (opcional si se usa endpoint por defecto)
- `API_AUTH` (opcional: header Authorization para la API)
- `ALLOWED_USER_IDS` (opcional, coma-separado)
- `STATUS_CHAT_ID` (opcional: chat que recibe la notificación de arranque)
- `WEBHOOK_URL` y `WEBHOOK_PATH` (opcional para webhook)

> Nota: No subir fichero `.env` a un repositorio público. No seas un monstruo Ve. Usa `gitignore` y GitHub Secrets para CI.

---

## Uso (local)
- Ejecutar (modo polling):
```bash
source venv/bin/activate
python main.py
```
---

## Uso (GitHub Actions)
El repo incluye un workflow `run_polling.yml` que:
- Ejecuta el bot en un runner de Actions por bloques (cron por defecto 3 horas).
- Establece tiempo máximo por job con `timeout-minutes`. de 180 minutos / 03 horas.
- Evita ejecuciones paralelas con `concurrency` para prevenir `409 Conflict`.

### Recomendaciones
- Añade `TELEGRAM_TOKEN` y otras variables como GitHub Secrets.
- Controlar `timeout-minutes` y `cron` para balancear disponibilidad vs. uso de minutos.

---

## Mensajes y formato
- El bot usa HTML en mensajes de notificación (evita errores de parseo en Markdown). 
- Para respuestas JSON largas, se envía como archivo adjunto si excede la longitud máxima de un mensaje.

---

## Seguridad y ética (no negociable)
- Esta herramienta es para análisis legítimo y cumplimiento de la ley. No se diseñó ni se debe usar para acceder ilegalmente a sistemas o para explotar vulnerabilidades.
- Si lo solicitas, este README no incluirá ni disimulará acciones inapropiadas (vulnerabilidades, IDOR o explotación).

---

## Buenas prácticas
- Mantén los secretos fuera del repositorio y usa GitHub Secrets para producción.
- Revisa los logs de GH Actions y remueve tokens/credenciales del historial en caso de exposiciones.
- Si planeas usar este bot en un entorno productivo, considera desplegar en un host que te permita alta disponibilidad y SSL, o usa webhooks con un servidor serverless.

---

## Contribuciones
- Pull requests bien explicadas y tests serán bienvenidas.
- Si agregas nuevos features, añade documentación y tests mínimos.

---

Hecho por Juan Felipe Oz *@JF0x0r* con mucho amor ome. 