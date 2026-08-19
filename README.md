# Solana Narrative Tracker

Escanea DexScreener en tiempo real, filtra memecoins de Solana bajo reglas de
bajo capital, y genera un bloque de texto listo para pegar en Claude
(gratuito o no) para pedir análisis de narrativa/rotación de dinero.

**No ejecuta ninguna operación.** Solo lee datos públicos de DexScreener y
genera un reporte de texto. La decisión y la ejecución en Photon (u otra
plataforma) siguen siendo manuales, tuyas.

## Cómo leer el reporte de cada corrida

1. Entra a la pestaña **Actions** de este repositorio.
2. Click en **Solana Narrative Tracker** (la lista de corridas, a la izquierda).
3. Click en la corrida más reciente (arriba del todo).
4. Click en el job **scan** → despliega el paso `Run python narrative_tracker.py`.
5. Ahí está el bloque de texto — cópialo y pégalo en tu chat de Claude.

## Cómo correrlo manualmente, sin esperar al horario

1. Pestaña **Actions** → **Solana Narrative Tracker**.
2. Botón **Run workflow** (arriba a la derecha) → **Run workflow** de nuevo para confirmar.
3. Espera ~15-30 segundos y actualiza la página — verás la corrida nueva arriba.

## Horario automático (hora Colombia, COT = UTC-5)

| Ventana | Para qué |
|---|---|
| **7:20am – 8:20am**, cada 10 min | Apertura del mercado / mapa de narrativas antes de que abra Wall Street (~8:00-8:30) |
| **1:45am – 5:00am**, cada 10 min | Madrugada americana — tokens recién creados, suelen volverse virales o acumular fuerza en estas horas |

⚠️ GitHub Actions es "mejor esfuerzo" en el horario programado — en horas
pico de la plataforma puede atrasarse unos minutos. No es un reloj atómico,
pero corre todos los días sin que tengas que mantener nada prendido.

## Cambiar el horario o la frecuencia

Edita `.github/workflows/narrative-tracker.yml`, sección `on: schedule:`.
Cada línea `cron:` es un horario en UTC (resta 5 horas a la hora de Colombia
para saber a qué hora UTC corresponde). [crontab.guru](https://crontab.guru)
ayuda a construir expresiones cron si quieres cambiar la frecuencia.

## Cambiar los filtros o las palabras clave de narrativa

Todo el criterio de filtrado (liquidez mínima, market cap mínimo, palabras
clave por narrativa) vive en `narrative_tracker.py` — es el mismo script
original, sin cambios de lógica, solo desplegado para correr solo.

## Costo

$0. El repo es público, así que los minutos de GitHub Actions no tienen
costo ni límite mensual. No hay API keys ni secretos — DexScreener es
público y no requiere autenticación.
