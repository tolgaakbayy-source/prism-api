from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import ccxt
import pandas as pd
import numpy as np
import talib

app = FastAPI(
    title="Prism API",
    version="1.0.0",
    description="Market Regime Intelligence API - Gerçek Binance verisi"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Binance bağlantısı
exchange = ccxt.binance()

def calculate_regime(symbol: str = "BTC/USDT"):
    """Binance'den gerçek veri çek ve regime hesapla"""
    try:
        # OHLCV verisi çek (son 100 mum)
        bars = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=100)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        closes = df['close'].values.astype(float)
        highs = df['high'].values.astype(float)
        lows = df['low'].values.astype(float)
        
        # ADX hesapla (trend gücü)
        adx = talib.ADX(highs, lows, closes, timeperiod=14)
        di_plus = talib.PLUS_DI(highs, lows, closes, timeperiod=14)
        di_minus = talib.MINUS_DI(highs, lows, closes, timeperiod=14)
        
        last_adx = adx[-1] if not np.isnan(adx[-1]) else 20
        
        # Trend yönü
        if last_adx > 25:
            if di_plus[-1] > di_minus[-1]:
                regime = "bull"
                score = min(0.95, 0.6 + (last_adx - 25) / 100)
            else:
                regime = "bear"
                score = min(0.95, 0.6 + (last_adx - 25) / 100)
        else:
            regime = "neutral"
            score = 0.5
        
        return {
            "regime": regime,
            "consensus_score": round(score, 2),
            "adx_value": round(last_adx, 2),
            "source": "Binance (gerçek veri)"
        }
    except Exception as e:
        return {
            "regime": "bull",
            "consensus_score": 0.85,
            "adx_value": 32.5,
            "source": "demo (hata: " + str(e)[:50] + ")"
        }

@app.get("/")
async def root():
    return {
        "product": "Prism API",
        "message": "Market Regime Intelligence",
        "status": "Gerçek Binance verisi ile canlı",
        "docs": "/docs"
    }

@app.get("/v1/regime")
async def get_regime(symbol: str = "BTCUSDT"):
    formatted_symbol = symbol[:3] + "/" + symbol[3:] if len(symbol) == 7 else symbol
    
    result = calculate_regime(formatted_symbol)
    
    return {
        "symbol": symbol,
        "timestamp": datetime.utcnow().isoformat(),
        "regime": result["regime"],
        "consensus_score": result["consensus_score"],
        "adx_value": result["adx_value"],
        "source": result["source"]
    }

@app.get("/v1/health")
async def health():
    return {"status": "alive", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)