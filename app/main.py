from fastapi import FastAPI
from . import models, database
from .routers import books

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Kitob APIsi")

app.include_router(books.router)

@app.get("/")
def root():
    return {"sms": "Xush kelibsiz! Kitob APIsiga!"}
