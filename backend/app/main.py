from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from .database import engine, Base
from .routers import auth, patients, appointments, payments, availability, reminders
from . import models

# Crear las tablas de la base de datos
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LoReyDent API",
    description="Sistema de Gestión Dental - API Backend",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    # En producción, cambiar "*" por el dominio específico: ["https://loreycontrol.irisvisual.com"]
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar Programador de Tareas
scheduler = BackgroundScheduler()
scheduler.add_job(reminders.process_reminders, 'cron', minute='*') # Revisar cada minuto
scheduler.start()

# Incluir routers
app.include_router(auth.router, prefix="/api")
app.include_router(patients.router, prefix="/api")
app.include_router(appointments.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(availability.router, prefix="/api")
app.include_router(reminders.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de LoReyDent"}

