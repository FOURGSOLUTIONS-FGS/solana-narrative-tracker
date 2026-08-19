import os
import requests
import json

# =====================================================================
# SOLANA NARRATIVE TRACKER - VERSÓN 100% GRATUITA (SIN API KEY)
# =====================================================================
# Este script escanea DexScreener en tiempo real, filtra los tokens
# bajo las reglas estrictas de bajo capital y genera un reporte listo
# para que lo copies y pegues en el Claude gratuito.
# =====================================================================

def obtener_tokens_tendencia_solana():
    """
    Obtiene pools reales de memecoins de Solana vía GeckoTerminal.

    ARREGLO (2026-08-19): la versión original buscaba la palabra literal
    "solana" en DexScreener (`/latest/dex/search?q=solana`) — eso devuelve
    sobre todo pares grandes como SOL/USDC (porque literalmente contienen
    la palabra "solana" en el nombre), no memecoins nuevas o en tendencia.
    Verificado en vivo: ese endpoint da 20 pares, casi ninguno pasa los
    filtros, y el reporte final sale vacío.

    GeckoTerminal es igual de gratuito y sin API key, pero consultando los
    DEX donde de verdad viven las memecoins ya graduadas (pumpswap, raydium,
    meteora, orca) en vez de buscar una palabra. Cada pool se traduce al
    mismo formato que usaba DexScreener (`chainId`/`baseToken`/`marketCap`/
    `liquidity`/`volume`) para que `procesar_y_categorizar` y
    `generar_bloque_copiado` sigan funcionando exactamente igual, sin tocar
    nada de la lógica de filtrado ni de narrativas.
    """
    print("[+] Conectando con la blockchain de Solana a través de GeckoTerminal...")
    dexes = ["pumpswap", "raydium", "meteora", "orca"]
    pairs = []
    for dex in dexes:
        url = f"https://api.geckoterminal.com/api/v2/networks/solana/dexes/{dex}/pools"
        try:
            response = requests.get(url, params={"page": 1}, timeout=10, headers={"Accept": "application/json"})
            if response.status_code == 200:
                for pool in response.json().get("data", []):
                    pairs.append(_pool_geckoterminal_a_formato_dexscreener(pool))
            else:
                print(f"[-] {dex}: HTTP {response.status_code}")
        except Exception as e:
            print(f"[-] Error de conexión con {dex}: {e}")
    return pairs


def _pool_geckoterminal_a_formato_dexscreener(pool):
    """Traduce un pool de GeckoTerminal a la misma forma de diccionario que
    devolvía DexScreener, para que el resto del script no necesite cambios."""
    attrs = pool.get("attributes", {}) or {}
    rel = pool.get("relationships", {}) or {}
    base_id = ((rel.get("base_token") or {}).get("data") or {}).get("id", "")
    mint = base_id.split("_", 1)[1] if "_" in base_id else base_id
    nombre = (attrs.get("name") or "").split(" / ")[0]  # "NVDA / SOL" -> "NVDA"

    # `market_cap_usd` suele venir null en tokens recién graduados de
    # pump.fun — `fdv_usd` casi siempre sí está poblado, así que sirve de
    # respaldo (mismo criterio que ya usa el proyecto en otros scripts).
    mcap = attrs.get("market_cap_usd") or attrs.get("fdv_usd") or 0
    volumen = attrs.get("volume_usd") or {}

    return {
        "chainId": "solana",
        "baseToken": {"address": mint, "symbol": nombre, "name": nombre},
        # Photon abre por dirección del PAR (`/en/lp/{pairAddress}`), no del
        # token — verificado en vivo navegando a
        # photon-sol.tinyastro.io/en/lp/<pairAddress> y confirmando que carga
        # el token correcto sin necesidad de conectar wallet. `attrs.address`
        # es la dirección del pool mismo, distinta del mint del token.
        "pairAddress": attrs.get("address"),
        "marketCap": float(mcap) if mcap else 0.0,
        "liquidity": {"usd": float(attrs.get("reserve_in_usd") or 0)},
        "volume": {
            "m5": float(volumen.get("m5") or 0),
            "h1": float(volumen.get("h1") or 0),
            "h24": float(volumen.get("h24") or 0),
        },
    }

# Los endpoints por-DEX de GeckoTerminal listan TODOS los pares, incluyendo
# contra monedas base que no son memecoins (SOL, USDC, USDT) — verificado en
# vivo: sin esto, "$SOL" aparecía como "candidato" en Otros Graduados.
MINTS_QUE_NO_SON_MEMECOINS = {
    "So11111111111111111111111111111111111111112",  # SOL (wrapped)
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
}


def procesar_y_categorizar(pairs):
    """
    Filtra los tokens según las métricas de tu presupuesto ($3 USD)
    y los agrupa en narrativas para facilitar el análisis.
    """
    categorizados = {
        "AI_Agents": [],          # Narrativa de Inteligencia Artificial
        "PolitiFi": [],           # Narrativa Política
        "Cute_Animals_Giga": [],  # Mascotas y Cultos de X
        "Otros_Graduados": []     # Otras tendencias con volumen
    }

    visitados = set()

    for p in pairs:
        # Solo operar tokens en la red de Solana
        if p.get('chainId') != 'solana':
            continue

        base_token = p.get('baseToken', {})
        address = base_token.get('address', '')
        symbol = base_token.get('symbol', '').upper()
        name = base_token.get('name', '').lower()

        # Evitar duplicados y monedas base que no son memecoins (SOL/USDC/USDT)
        if address in visitados or address in MINTS_QUE_NO_SON_MEMECOINS:
            continue
        visitados.add(address)

        mcap = p.get('marketCap', 0)
        liquidity = p.get('liquidity', {}).get('usd', 0)
        vol_5m = p.get('volume', {}).get('m5', 0)
        vol_1h = p.get('volume', {}).get('h1', 0)
        vol_24h = p.get('volume', {}).get('h24', 0)

        # ==========================================
        # FILTROS DE SEGURIDAD PARA TU CAPITAL ($3 USD)
        # ==========================================
        # 1. Liquidez mínima de $35,000 USD para que no te quedes atrapado sin poder vender
        if liquidity < 35000:
            continue

        # 2. Capitalización de mercado mínima para evitar tokens fantasmas
        if mcap < 100000:
            continue

        pair_address = p.get('pairAddress', '')
        token_info = {
            "symbol": symbol,
            "address": address,
            "pair_address": pair_address,
            # Link directo que abre el token en Photon sin tener que buscarlo
            # a mano — Photon usa la dirección del PAR, no la del token (ver
            # `_pool_geckoterminal_a_formato_dexscreener`), verificado
            # navegando en vivo a esta URL con un pair_address real. Si por
            # algún motivo GeckoTerminal no trae pair_address (no debería
            # pasar, pero por si acaso), se deja vacío en vez de inventar
            # una URL sin probar — mejor "no salió link" que un link roto.
            "photon_url": (
                f"https://photon-sol.tinyastro.io/en/lp/{pair_address}" if pair_address else ""
            ),
            "mcap": f"${mcap:,.0f}" if mcap else "N/D",
            "liquidity": f"${liquidity:,.0f}",
            "vol_5m": f"${vol_5m:,.0f}",
            "vol_1h": f"${vol_1h:,.0f}",
            "vol_24h": f"${vol_24h:,.0f}"
        }

        # Clasificación por palabras clave de la narrativa
        name_and_symbol = (name + " " + symbol.lower())
        if any(kw in name_and_symbol for kw in ["goat", "agent", "ai", "truth", "terminal", "fart", "gpts", "eliza", "solanaai"]):
            categorizados["AI_Agents"].append(token_info)
        elif any(kw in name_and_symbol for kw in ["trump", "melania", "biden", "harris", "maga", "fight", "usa"]):
            categorizados["PolitiFi"].append(token_info)
        elif any(kw in name_and_symbol for kw in ["dog", "cat", "wif", "michi", "pengu", "giga", "sigma", "chill", "popcat"]):
            categorizados["Cute_Animals_Giga"].append(token_info)
        else:
            # Si tiene muy buen volumen en 5 minutos, va a "Otros"
            if vol_5m > 5000:
                categorizados["Otros_Graduados"].append(token_info)

    return categorizados

def generar_bloque_copiado(categorizados):
    """
    Crea el texto formateado en Markdown limpio diseñado específicamente
    para que lo copies del terminal de Replit y lo pegues en tu Claude gratis.
    """
    markdown = []
    markdown.append("# 🚨 SOLANA LIVE ON-CHAIN DATA (PARA ANÁLISIS DE TRINCHERA)\n")
    markdown.append("Actúa como mi analista de riesgo de memecoins. A continuación te pego los datos en tiempo real de los tokens que cumplen con mis filtros de bajo capital ($3 USD de saldo, compras de 0.01 SOL).")
    markdown.append("Por favor, analiza la rotación del dinero y dime cuál narrativa tiene mayor fuerza en este momento y en qué token específico del listado debería enfocar mi Photon para hacer un scalping rápido (+15% a +20%).\n")

    for categoria, tokens in categorizados.items():
        if not tokens:
            continue
        markdown.append(f"## 📌 NARRATIVA: {categoria.replace('_', ' ')}")
        for idx, t in enumerate(tokens[:5]):  # Mostrar los top 5 de cada categoría para no saturar
            markdown.append(f"{idx+1}. **${t['symbol']}**")
            markdown.append(f"   * Contrato: `{t['address']}`")
            if t.get("photon_url"):
                # Click directo — abre el token en Photon sin buscarlo a mano.
                markdown.append(f"   * 🔫 [Abrir en Photon]({t['photon_url']})")
            markdown.append(f"   * Market Cap: {t['mcap']} | Liquidez: {t['liquidity']}")
            markdown.append(f"   * Vol 5m: {t['vol_5m']} | Vol 1h: {t['vol_1h']}")
            markdown.append("")

    markdown.append("---")
    markdown.append("Analiza detalladamente estos datos bajo las reglas de Domin y Wood (baja tenencia, evitar bundling, priorizar volumen en 5m sobre Mcap). ¡Dame mi plan de batalla rápido!")

    return "\n".join(markdown)

if __name__ == "__main__":
    raw_pairs = obtener_tokens_tendencia_solana()
    if raw_pairs:
        datos_filtrados = procesar_y_categorizar(raw_pairs)
        reporte_final = generar_bloque_copiado(datos_filtrados)

        # Limpiar consola e imprimir el resultado listo para copiar
        print("\n" + "="*60)
        print("¡ESCÁNER COMPLETADO CON ÉXITO!")
        print("COPIA TODO EL TEXTO DE ABAJO Y PÉGALO EN TU CHAT DE CLAUDE:")
        print("="*60 + "\n")
        print(reporte_final)
        print("\n" + "="*60)

        # Además del log de consola, se guarda en un archivo del repo — así
        # el reporte más reciente siempre está en la MISMA URL, sin tener
        # que navegar los logs de GitHub Actions para encontrarlo.
        with open("reporte.md", "w", encoding="utf-8") as f:
            f.write(reporte_final)
        print("\n[+] Guardado en reporte.md")
    else:
        print("[-] No se pudieron recuperar datos en este turno. Intenta de nuevo en unos segundos.")
