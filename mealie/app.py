from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import startup
from routes import (
    backup_routes,
    meal_routes,
    migration_routes,
    recipe_routes,
    setting_routes,
    static_routes,
    user_routes,
)
from settings import PORT, PRODUCTION, WEB_PATH, docs_url, redoc_url
from utils.logger import logger

startup.pre_start()

app = FastAPI(
    title="Mealie",
    description="A place for all your recipes",
    version="0.0.1",
    docs_url=docs_url,
    redoc_url=redoc_url,
)

# Mount Vue Frontend only in production
if PRODUCTION:
    app.mount("/static", StaticFiles(directory=WEB_PATH, html=True))

# API Routes
app.include_router(recipe_routes.router)
app.include_router(meal_routes.router)
app.include_router(setting_routes.router)
app.include_router(backup_routes.router)
app.include_router(user_routes.router)
app.include_router(migration_routes.router)

# API 404 Catch all CALL AFTER ROUTERS
@app.get("/api/{full_path:path}", status_code=404, include_in_schema=False)
def invalid_api():
    return None


app.include_router(static_routes.router)


# Generate API Documentation
if not PRODUCTION:
    startup.generate_api_docs(app)

if __name__ == "__main__":
    logger.info("-----SYSTEM STARTUP-----")

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=PORT,
        reload=True,
        debug=True,
        workers=1,
        forwarded_allow_ips="*",
    )
