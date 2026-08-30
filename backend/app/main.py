import os
import asyncpg
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="Compliance & Policy Copilot")

DATABASE_URL = os.getenv("DATABASE_URL")


@app.get("/health")
async def health():
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        result = await conn.fetchval("SELECT 1")
        await conn.close()
        return {"status": "ok", "db": "connected", "check": result}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"DB connection failed: {e}")





