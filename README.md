# Nexora Bot

Bot de Telegram y panel web para Nexora.

Dueño oficial: `@PeruDoxer`  
ID dueño: `7454664711`

## Railway

Usa dos servicios desde este repo:

- `web`: `gunicorn -w 2 -b 0.0.0.0:$PORT app:app`
- `worker`: `python main.py`

Variables recomendadas en ambos servicios:

```text
NEXORA_INTERNAL_API_KEY=pon_un_secret_largo
NEXORA_PANEL_SECRET=pon_otro_secret_largo
NEXORA_PANEL_USER=admin
NEXORA_PANEL_PASSWORD=una_clave_larga
NEXORA_PANEL_PUBLIC=true
NEXORA_ADMIN_ID=7454664711
NEXORA_BOT_NAME=#NEXORA ⇒
TOKEN_BOT=tu_token_del_bot
```

Solo en `worker`:

```text
NEXORA_API_BASE=https://tu-servicio-web.up.railway.app
```

Si usas SQLite con volumen:

```text
NEXORA_DATA_DIR=/data
```

Los nombres viejos `SPIDERSYN_*` siguen funcionando como compatibilidad, pero el repo nuevo debe usar `NEXORA_*`.

## Validación local

```bash
python -m compileall -q .
python -m unittest discover -s tests
```
