#!/usr/bin/env python
import os
from app import app
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

if __name__ == "__main__":
    # Obtener el puerto desde la variable de entorno o usar 5000 por defecto
    port = int(os.environ.get('PORT', 5000))
    
    # Opciones de ejecución inseguras para entorno de desarrollo
    app.run(host='0.0.0.0', port=port, debug=True)