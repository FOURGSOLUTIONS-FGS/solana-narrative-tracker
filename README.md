# Solana Narrative Tracker

Escanea GeckoTerminal en tiempo real (pools establecidos + recién creados),
filtra memecoins de Solana bajo reglas de bajo capital, y genera un bloque
de texto listo para pegar en Claude (gratuito o no) para pedir análisis de
narrativa/rotación de dinero — con link directo a Photon por cada token.

**No ejecuta ninguna operación.** Solo lee datos públicos y genera un
reporte de texto. La decisión y la ejecución en Photon siguen siendo
manuales, tuyas.

## Sección prioritaria: 🔥 Nuevos Momentum

Además de las narrativas de siempre, el reporte trae una sección aparte,
primero: tokens creados hace **menos de 48 horas** que ya tienen volumen
real en los últimos 5 minutos — candidatos a scalping en el momento mismo
de la corrida, ordenados por actividad reciente (el más movido primero).
Cada uno muestra su **edad exacta** (días/horas/minutos desde que se creó
el pool).

⚠️ Esto es intencionalmente más agresivo que la "regla de 48h" de esperar
antes de comprar — es al revés, prioriza justo lo que todavía no cumplió
esas 48h. Es una decisión explícita para cazar el tramo donde vive el
scalping, no un descuido. El riesgo es mayor precisamente por eso: este
script no verifica seguridad del contrato (mint/freeze authority, liquidez
bloqueada, concentración de holders) — solo edad, liquidez y volumen. La
verificación de seguridad sigue siendo manual (Photon/Rugcheck) antes de
entrar a cualquiera de estos.

## Cómo leer el reporte — un solo link fijo

**[Abrir el reporte más reciente](reporte.md)** — siempre la misma URL. Cada
corrida lo sobreescribe automáticamente y lo sube al repo; solo entras a ese
link, GitHub lo muestra ya formateado, y copias el texto de ahí.

No hace falta entrar a la pestaña Actions para nada del día a día — eso solo
sirve si algo falla y quieres ver el detalle técnico (ver abajo).

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

## Si algo falla (reporte.md no se actualiza)

1. Pestaña **Actions** → **Solana Narrative Tracker** → la corrida más reciente.
2. Si tiene una ❌ roja, click en el job **scan** para ver en qué paso falló.
3. Lo más probable: GeckoTerminal tardó más de 10s en responder (raro) o
   hubo un límite de rate temporal — la siguiente corrida (10 min después)
   normalmente se recupera sola.

## Costo

$0. El repo es **público**, así que los minutos de GitHub Actions no tienen
costo ni límite mensual, sin importar cuántas veces corra al día. No hay API
keys ni secretos propios — DexScreener/GeckoTerminal son públicos y no
requieren autenticación. (El único contenido del repo es el script de
filtrado y los reportes generados — nada sensible que proteger con
privacidad.)
