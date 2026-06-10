from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="Prism API", version="1.0.0")

@app.get("/")
async def root():
    return {"product": "Prism API", "message": "Market Regime Intelligence"}

@app.get("/v1/regime")
async def get_regime(symbol: str = "BTCUSDT"):
    return {
        "symbol": symbol,
        "timestamp": datetime.utcnow().isoformat(),
        "regime": "bull",
        "consensus_score": 0.85
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000)