from config.app import app
from routers import init,auth,messages,dashboard

app.include_router(dashboard.router)
app.include_router(auth.router)
app.include_router(init.router)
app.include_router(messages.router)

@app.get("/")
async def root():
  return {"message": "Hello World"}