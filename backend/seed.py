from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash
import sys

def seed():
    db = SessionLocal()
    try:
        # Verificar si ya existe el usuario
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            print("El usuario admin ya existe.")
            return

        new_user = User(
            username="admin",
            email="admin@loreydent.com",
            full_name="Administrador LoReyDent",
            hashed_password=get_password_hash("admin123")
        )
        db.add(new_user)
        db.commit()
        print("Usuario admin creado exitosamente.")
        print("Usuario: admin")
        print("Contraseña: admin123")
    except Exception as e:
        print(f"Error al crear el usuario: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()

