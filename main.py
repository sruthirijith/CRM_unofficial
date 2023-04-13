import uvicorn
from fastapi import FastAPI,  Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session


from config.base import settings
from core.api.sales_person import sales_person_api
from core.api.super_admin import super_admin_api
from core.api.admin import admin_api
from core.database.connection import get_db, Base, engine
from core.models.models import Country, IDProofs

app = FastAPI()

origins = ["http://localhost:5000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(sales_person_api.router)
app.include_router(super_admin_api.router)
app.include_router(admin_api.router)

@app.get("/")
async def home():
    return {"XPayBack CRM APIs"}


