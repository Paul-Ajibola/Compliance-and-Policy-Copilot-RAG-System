from fastapi import FastAPI, HTTPException
from app.config import settings
from app.db.session import check_db_connection



# instantiate FastAPI
app = FastAPI(title="Compliance & Policy Copilot")


# the health status API check
@app.get("/health")
async def health():
    db_ok = await check_db_connection()
    if not db_ok:
        raise HTTPException(status_code=503, detail="DB connection failed")
    return {"status": "ok", "db": "connected", "environment": settings.environment}

    