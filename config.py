import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configuración para la base de datos
class Config:
    # URL de conexión para PostgreSQL
    # Si la variable DATABASE_URL no está en el entorno, se usa la URL por defecto
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/vulnerable_blog')
    
    # Si la URL comienza con "postgres://", reemplazarla por "postgresql://" para compatibilidad con SQLAlchemy
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    
    # Desactivar el seguimiento de modificaciones para mejorar el rendimiento
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Clave secreta para la aplicación
    # Vulnerabilidad: Clave secreta débil y hardcodeada
    SECRET_KEY = "super_insecure_secret_key"
    
    # Modo debug activado (otra vulnerabilidad en entorno de producción)
    DEBUG = True