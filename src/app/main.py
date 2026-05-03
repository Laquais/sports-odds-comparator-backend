from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, odds, freebets, bets

app = FastAPI(
    title="Sports Odds Comparison API",
    description="API pour comparer les cotes des bookmakers",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(odds.router)
app.include_router(freebets.router)
app.include_router(bets.router)

@app.get("/")
def read_root():
    return {
        "message": "Sports Odds Comparison API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
