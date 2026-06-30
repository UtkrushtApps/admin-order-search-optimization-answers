from fastapi import FastAPI

from app.api.routes import router
from app.db.session import install_query_counter

install_query_counter()

app = FastAPI(title="Admin Orders API", version="1.0.0")
app.include_router(router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
