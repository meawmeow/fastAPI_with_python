from fastapi import Depends, FastAPI

from routers import items,bgtask
from auths import authJwt


app = FastAPI(
    title="My Learn FastAPI",
    description="This is a very fancy project, with auto docs for the API and everything",
)

app.include_router(items.router)
app.include_router(bgtask.router, 
    prefix="/task",
    tags=[" background task"])
app.include_router(authJwt.router,
    prefix="/admin",
    tags=["Authentication"])

@app.get("/",tags=["Main"])
async def root():
    return {"message": "Hello Home Applications!"}