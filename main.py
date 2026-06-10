from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import ccxt
import pandas as pd
import numpy as np
import talib

app = FastAPI(title="Prism API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

exchange = ccxt.binance()

@app.get("/")
async def root():
    return {"product": "Prism API", "message": "Market Regime Intelligence"}

@app.get("/v1/regime")
async def get_regime(symbol: str = "BTCUSDT"):
    try:
        formatted = symbol[:3] + "/" + symbol[3:] if len(symbol) == 7 else symbol
        bars = exchange.fetch_ohlcv(formatted, timeframe='1h', limit=100)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        closes = df['close'].values.astype(float)
        highs = df['high'].values.astype(float)
        lows = df['low'].values.astype(float)
        
        adx = talib.ADX(highs, lows, closes, timeperiod=14)
        di_plus = talib.PLUS_DI(highs, lows, closes, timeperiod=14)
        di_minus = talib.MINUS_DI(highs, lows, closes, timeperiod=14)
        
        last_adx = adx[-1] if not np.isnan(adx[-1]) else 20
        
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
            "symbol": symbol,
            "timestamp": datetime.utcnow().isoformat(),
            "regime": regime,
            "consensus_score": round(score, 2),
            "adx_value": round(last_adx, 2)
        }
    except Exception as e:
        return {"symbol": symbol, "regime": "neutral", "consensus_score": 0.5, "error": str(e)[:100]}

@app.get("/v1/health")
async def health():
    return {"status": "alive"}