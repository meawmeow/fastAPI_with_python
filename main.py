from fastapi import Depends, FastAPI

from routers import items
from auths import authJwt

app = FastAPI()

app.include_router(items.router)
app.include_router(authJwt.router,
    prefix="/admin",
    tags=["Authentication"])

@app.get("/",tags=["Main"])
async def root():
    return {"message": "Hello Home Applications!"}