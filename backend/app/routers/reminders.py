from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import pytz
from twilio.rest import Client
from .. import models, schemas, database, auth

router = APIRouter(prefix="/reminders", tags=["Recordatorios"])

def get_twilio_client(db: Session):
    config = db.query(models.ReminderConfig).first()
    if not config or not config.twilio_sid or not config.twilio_token:
        return None, None
    try:
        return Client(config.twilio_sid, config.twilio_token), config.twilio_phone
    except Exception:
        return None, None

@router.get("/config", response_model=schemas.ReminderConfig)
async def get_config(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    config = db.query(models.ReminderConfig).first()
    if not config:
        config = models.ReminderConfig()
        db.add(config)
        db.commit()
        db.refresh(config)
    return config

@router.post("/config", response_model=schemas.ReminderConfig)
async def update_config(config_in: schemas.ReminderConfigCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    config = db.query(models.ReminderConfig).first()
    if not config:
        config = models.ReminderConfig()
        db.add(config)
    
    for field, value in config_in.model_dump().items():
        if value is not None:
            setattr(config, field, value)
    
    db.commit()
    db.refresh(config)
    return config

def send_whatsapp(to: str, message: str, client: Client, from_number: str):
    try:
        # Twilio WhatsApp numbers must be in the format 'whatsapp:+1234567890'
        # Limpiar el número de espacios y guiones
        clean_to = "".join(filter(str.isdigit, to))
        if not clean_to.startswith("+"):
            # Asumir México (+52) si no tiene signo + y tiene 10 dígitos
            if len(clean_to) == 10:
                clean_to = "+52" + clean_to
            else:
                clean_to = "+" + clean_to
        
        formatted_to = f"whatsapp:{clean_to}"
        formatted_from = f"whatsapp:{from_number}" if from_number.startswith("+") else f"whatsapp:+{from_number}"
        
        client.messages.create(
            body=message,
            from_=formatted_from,
            to=formatted_to
        )
        return True
    except Exception as e:
        print(f"Error sending WhatsApp to {to}: {e}")
        return False

# background task to be called by APScheduler
def process_reminders():
    db = database.SessionLocal()
    try:
        config = db.query(models.ReminderConfig).first()
        if not config or not config.is_active:
            return

        client, from_number = get_twilio_client(db)
        if not client:
            return

        # Usar zona horaria de México
        tz = pytz.timezone('America/Mexico_City')
        now = datetime.now(tz)
        current_time = now.strftime("%H:%M")
        today_date = now.date()

        # 1. Dentist Reminders (Today's agenda)
        if current_time == config.dentist_reminder_time:
            dentists = db.query(models.User).filter(models.User.phone != None).all()
            if dentists:
                # Get today's appointments
                start_today = datetime.combine(today_date, datetime.min.time())
                end_today = datetime.combine(today_date, datetime.max.time())
                
                appointments = db.query(models.Appointment).filter(
                    models.Appointment.date_time >= start_today,
                    models.Appointment.date_time <= end_today,
                    models.Appointment.status == "pendiente"
                ).all()
                
                if appointments:
                    msg = f"📍 Agenda LoReyDent Hoy ({today_date.strftime('%d/%m/%Y')}):\n"
                    for appt in appointments:
                        time_str = appt.date_time.strftime("%H:%M")
                        msg += f"- {time_str}: {appt.patient.first_name} {appt.patient.last_name} ({appt.location})\n"
                    
                    for dentist in dentists:
                        send_whatsapp(dentist.phone, msg, client, from_number)
            
            config.last_run_dentist = now.replace(tzinfo=None)
            db.commit()

        # 2. Patient Reminders (Tomorrow - Day Before)
        if current_time == config.patient_reminder_day_before_time:
            tomorrow = today_date + timedelta(days=1)
            start_tomorrow = datetime.combine(tomorrow, datetime.min.time())
            end_tomorrow = datetime.combine(tomorrow, datetime.max.time())
            
            tomorrow_appts = db.query(models.Appointment).filter(
                models.Appointment.date_time >= start_tomorrow,
                models.Appointment.date_time <= end_tomorrow,
                models.Appointment.status == "pendiente"
            ).all()
            
            for appt in tomorrow_appts:
                if appt.patient.phone:
                    time_str = appt.date_time.strftime("%H:%M")
                    msg = f"🦷 Hola {appt.patient.first_name}, te recordamos tu cita en LoReyDent mañana {tomorrow.strftime('%d/%m')} a las {time_str} en sucursal {appt.location}. ¡Te esperamos!"
                    send_whatsapp(appt.patient.phone, msg, client, from_number)
            
            config.last_run_patient_before = now.replace(tzinfo=None)
            db.commit()

        # 3. Patient Reminders (Today - Morning)
        if current_time == config.patient_reminder_day_of_time:
            start_today = datetime.combine(today_date, datetime.min.time())
            end_today = datetime.combine(today_date, datetime.max.time())
            
            today_appts = db.query(models.Appointment).filter(
                models.Appointment.date_time >= start_today,
                models.Appointment.date_time <= end_today,
                models.Appointment.status == "pendiente"
            ).all()
            
            for appt in today_appts:
                if appt.patient.phone:
                    time_str = appt.date_time.strftime("%H:%M")
                    msg = f"🦷 Hola {appt.patient.first_name}, hoy tienes una cita en LoReyDent a las {time_str}. ¡Nos vemos pronto!"
                    send_whatsapp(appt.patient.phone, msg, client, from_number)
            
            config.last_run_patient_today = now.replace(tzinfo=None)
            db.commit()
            
    except Exception as e:
        print(f"Error in background task: {e}")
    finally:
        db.close()
