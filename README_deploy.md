# Despliegue con GitHub Actions — Polling (sin host)

NOTA: Esta configuración usa GitHub Actions _como_ runner para ejecutar el bot por periodos (cada 4 horas por defecto). No es 24/7: el job corre el tiempo que definas (max 6 horas por job en runners de GitHub). Si necesitas disponibilidad 24/7 considera un host (Fly.io, Render, Cloud Run).

## 1. Preparar repo local
Si tu proyecto no está en Git:

```bash
# dentro de la carpeta del proyecto
git init
git add -A
git commit -m "Initial commit"
# Cambia 'main' si tu rama principal tiene otro nombre
git branch -M main
```

## 2. Crear un repo en GitHub
Puedes hacerlo con la web UI o `gh` CLI.

Con GitHub CLI (si lo tienes):
```bash
gh repo create <OWNER>/<REPO> --public --source=. --remote=origin --push
```
O por GitHub Web: https://github.com/new — crea el repo, luego agrega la URL remota:
```bash
git remote add origin git@github.com:<OWNER>/<REPO>.git
git push -u origin main
```

## 3. Añadir secrets en tu repo de GitHub
Ve a: `Settings > Secrets and variables > Actions > New repository secret`.
Agrega al menos:
- `TELEGRAM_TOKEN` — el token de tu bot
- `API_URL` — (si tu script lo usa; si no, déjalo vacío)
- `API_AUTH` — (si tu script lo usa)
- `ALLOWED_USER_IDS` — (opcional)

También puedes usar `gh` CLI:
```bash
# desde tu repo local
gh secret set TELEGRAM_TOKEN --body "${TELEGRAM_TOKEN}"
gh secret set API_URL --body "${API_URL}"
# etc.
```

## 4. Revisar y cambiar el workflow si lo deseas
El archivo `./github/workflows/run_polling.yml` ejecutará el bot en polling. Por defecto está programado cada 4 horas y con timeout de 6 horas. Ajusta `cron` y `timeout-minutes` si quieres.

## 5. Inicio y pruebas
- Push a GitHub: `git push origin main`.
- Ve a la pestaña "Actions" en GitHub para ver los workflows; podrás lanzar manualmente desde "Run workflow" (botón a la derecha) o esperar al cron.
- Ver los logs en la ejecución: allí verás la salida del script (pero ten cuidado de no imprimir secretos en logs).

## 6. Cosas a tener en cuenta y recomendaciones
- Evitar ejecuciones paralelas: el workflow tiene `concurrency` configurado y `cancel-in-progress: true` para evitar dos jobs en paralelo (previene `Conflict` de Telegram).
- Si necesitas pruebas live con Webhook, usa ngrok para pruebas locales o despliega a un host.
- Monitorea tu uso de minutos de GitHub Actions si usas una cuenta gratuita.

## 7. Parar el bot (si hace falta desde Actions)
- Si ejecutas mediante cron, el runner parará automáticamente en `timeout-minutes`.
- Si hay un job en ejecución y deseas cancelarlo, ve a `Actions` -> tu workflow -> `Cancel run`.

---

Si quieres que cree el repo en GitHub (si me das el nombre) y suba los archivos, puedo asistirte con pasos interactivos.
