from fastapi import FastAPI

from auth.src.presentation.http.router import router

app = FastAPI(title="Auth Service", version="0.0.1")

app.include_router(router)
