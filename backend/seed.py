from app.database import SessionLocal
from app.models import User, Patient
from app.auth import get_password_hash
import sys

def seed():
    db = SessionLocal()
    try:
        # ── Usuarios ──────────────────────────────────────────────────────────
        users = [
            {
                "username": "javier",
                "email": "javier@loreydent.com",
                "full_name": "Javier López",
                "password": "javierpassword"
            },
            {
                "username": "katia",
                "email": "katia@loreydent.com",
                "full_name": "Katia González",
                "password": "katiapassword"
            },
            {
                "username": "recepcion",
                "email": "recepcion@loreydent.com",
                "full_name": "Recepcionista",
                "password": "recepcionpassword"
            }
        ]

        for user_data in users:
            existing = db.query(User).filter(User.username == user_data["username"]).first()
            if not existing:
                new_user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    full_name=user_data["full_name"],
                    hashed_password=get_password_hash(user_data["password"])
                )
                db.add(new_user)
                print(f"Usuario {user_data['username']} creado exitosamente.")
            else:
                print(f"El usuario {user_data['username']} ya existe.")

        db.commit()
        print("Usuarios procesados. Iniciando pacientes...")

        # ── Pacientes ficticios de prueba ────────────────────────────────────
        demo_patients = [
            {
                "first_name": "María",
                "last_name": "Hernández Ruiz",
                "phone": "951-234-5678",
                "email": "maria.hernandez@email.com",
                "age": 34,
                "sex": "Femenino",
                "address": "Calle Reforma 45, Oaxaca",
                "consultation_reason": "Revisión general y limpieza dental",
                "entry_date": "2026-01-15",
                "blood_pressure": "120/80",
            },
            {
                "first_name": "Carlos",
                "last_name": "López Mendoza",
                "phone": "951-876-5432",
                "email": "carlos.lopez@email.com",
                "age": 28,
                "sex": "Masculino",
                "address": "Av. Independencia 112, Miahuatlán",
                "consultation_reason": "Dolor de muela y extracción",
                "entry_date": "2026-02-20",
                "blood_pressure": "118/76",
            },
            {
                "first_name": "Ana Sofía",
                "last_name": "Martínez García",
                "phone": "951-456-7890",
                "email": "anasofia.martinez@email.com",
                "age": 42,
                "sex": "Femenino",
                "address": "Prolongación Juárez 78, Oaxaca",
                "consultation_reason": "Ortodoncia y evaluación",
                "entry_date": "2026-03-10",
                "blood_pressure": "125/82",
            },
            {
                "first_name": "Roberto",
                "last_name": "Gómez Bolaños",
                "phone": "951-111-2222",
                "email": "roberto.gomez@email.com",
                "age": 55,
                "sex": "Masculino",
                "address": "Calle del Chavo 8, Oaxaca",
                "consultation_reason": "Prótesis dental",
                "entry_date": "2026-04-01",
                "blood_pressure": "130/85",
            },
            {
                "first_name": "Lucía",
                "last_name": "Torres Valdez",
                "phone": "951-333-4444",
                "email": "lucia.torres@email.com",
                "age": 25,
                "sex": "Femenino",
                "address": "Colonia Reforma, Oaxaca",
                "consultation_reason": "Blanqueamiento dental",
                "entry_date": "2026-04-10",
                "blood_pressure": "115/75",
            },
            {
                "first_name": "Miguel Ángel",
                "last_name": "Ruiz Pineda",
                "phone": "951-555-6666",
                "email": "miguel.ruiz@email.com",
                "age": 38,
                "sex": "Masculino",
                "address": "Calle Hidalgo 20, Miahuatlán",
                "consultation_reason": "Endodoncia",
                "entry_date": "2026-04-20",
                "blood_pressure": "122/80",
            },
        ]

        for p_data in demo_patients:
            existing = db.query(Patient).filter(
                Patient.first_name == p_data["first_name"],
                Patient.last_name == p_data["last_name"]
            ).first()
            if not existing:
                new_patient = Patient(**p_data)
                db.add(new_patient)
                print(f"Paciente {p_data['first_name']} {p_data['last_name']} creado.")
            else:
                print(f"Paciente {p_data['first_name']} {p_data['last_name']} ya existe.")

        db.commit()
        print("Seed completado exitosamente.")

    except Exception as e:
        print(f"Error al ejecutar seed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
