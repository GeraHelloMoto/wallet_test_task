from fastapi import FastAPI
from app.routes import wallets

app = FastAPI(title="Wallet API")
app.include_router(wallets.router)