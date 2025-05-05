# Blog de Ciberseguridad (Intencionalmente Vulnerable)

Esta es una aplicación web **intencionalmente vulnerable** creada con fines educativos para demostrar vulnerabilidades web comunes y cómo pueden ser detectadas por herramientas de escaneo como el escáner de vulnerabilidades.

## ⚠️ ADVERTENCIA

**Esta aplicación contiene vulnerabilidades de seguridad intencionales. No la utilice en un entorno de producción ni ingrese información real o sensible en ella.**

## Vulnerabilidades implementadas

La aplicación contiene las siguientes vulnerabilidades intencionales:

1. **SQL Injection**: En la funcionalidad de búsqueda y autenticación
   - Rutas: `/search?q=`, `/login`, `/post/<id>`
   - Ejemplo: `' OR '1'='1` en el formulario de búsqueda muestra todos los artículos

2. **Cross-Site Scripting (XSS)**: En los comentarios de los artículos
   - Ruta: `/post/<id>` (formulario de comentarios)
   - Ejemplo: `<script>alert('XSS')</script>` en un comentario

3. **Cross-Site Request Forgery (CSRF)**: En la actualización de perfil
   - Ruta: `/profile` (formulario de cambio de contraseña)
   - Demo: Archivo `static/csrf-demo.html`

4. **Clickjacking**: Falta de encabezado X-Frame-Options
   - Afecta a toda la aplicación
   - Demo: Archivo `static/clickjacking-demo.html`

5. **Open Redirect**: En la funcionalidad de redirección
   - Ruta: `/redirect?url=https://example.com`
   - Ejemplo: `/redirect?url=https://sitio-malicioso.com`

6. **Headers de Seguridad Faltantes**: No implementa headers de seguridad importantes
   - Faltan: X-Frame-Options, Content-Security-Policy, X-Content-Type-Options, etc.

## Requisitos

- Python 3.8 o superior
- PostgreSQL

## Instalación y Ejecución Local

1. **Clonar el repositorio**

2. **Configurar PostgreSQL**:
   - Instalar PostgreSQL si no lo tiene instalado
   - Crear una base de datos: `createdb vulnerable_blog`

3. **Configurar variables de entorno**:
   - Crear un archivo `.env` en la raíz del proyecto con el siguiente contenido:
   ```
   DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/vulnerable_blog
   PORT=5000
   FLASK_APP=app.py
   FLASK_ENV=development
   ```

4. **Instalar dependencias**:
   ```
   pip install -r requirements.txt
   ```

5. **Inicializar la base de datos**:
   ```
   python init_db.py
   ```

6. **Ejecutar la aplicación**:
   ```
   python run.py
   ```

7. **Acceder a la aplicación**:
   Abra su navegador y vaya a `http://127.0.0.1:5000`

## Migración desde SQLite (si es necesario)

Si tienes datos en una base de datos SQLite existente que deseas migrar a PostgreSQL:

1. Asegúrate de configurar correctamente la variable de entorno `DATABASE_URL` en el archivo `.env`
2. Ejecuta el script de migración:
   ```
   python migrate_data.py
   ```

## Credenciales por defecto

- **Usuario**: admin
- **Contraseña**: admin123

## Despliegue en Railway

Para desplegar esta aplicación en Railway:

1. **Crear cuenta en Railway**:
   - Registra una cuenta en [Railway](https://railway.app/)

2. **Instalar CLI de Railway** (opcional):
   ```
   npm i -g @railway/cli
   railway login
   ```

3. **Iniciar un nuevo proyecto**:
   - Desde la interfaz web de Railway, crea un nuevo proyecto
   - Haz clic en "Deploy from GitHub repo"
   - Selecciona el repositorio

4. **Agregar servicio PostgreSQL**:
   - En el proyecto, haz clic en "New"
   - Selecciona "Database" y luego "PostgreSQL"

5. **Configurar variables de entorno** (opcional, Railway lo hace automáticamente):
   - Railway configura automáticamente `DATABASE_URL`
   - Si necesitas variables adicionales, puedes agregarlas en la sección "Variables"

6. **Desplegar la aplicación**:
   - Railway detectará automáticamente el archivo `Procfile` y desplegará la aplicación
   - La aplicación utilizará la base de datos PostgreSQL proporcionada por Railway

## Estructura del proyecto

```
├── app.py                # Aplicación principal Flask
├── config.py             # Configuración de la aplicación
├── init_db.py            # Script para inicializar la base de datos
├── migrate_data.py       # Script para migrar datos desde SQLite
├── Procfile              # Configuración para Railway/Heroku
├── railway.json          # Configuración específica para Railway
├── README.md             # Documentación
├── requirements.txt      # Dependencias del proyecto
├── run.py                # Script para ejecutar la aplicación
└── static/               # Archivos estáticos
    ├── clickjacking-demo.html  # Demo de ataque clickjacking
    └── csrf-demo.html          # Demo de ataque CSRF
└── templates/            # Plantillas HTML
    ├── about.html
    ├── index.html
    ├── layout.html
    ├── login.html
    ├── post.html
    ├── profile.html
    ├── register.html
    └── search.html
```

## Uso con el Escáner de Vulnerabilidades

Esta aplicación está diseñada para ser analizada con el escáner de vulnerabilidades. Para probar el escáner:

1. Despliega esta aplicación vulnerable en Railway
2. Utiliza la URL de despliegue como objetivo en el escáner de vulnerabilidades
3. Ejecuta el escaneo y verifica los resultados
4. El escáner debería detectar todas las vulnerabilidades implementadas

## Propósito Educativo

Esta aplicación ha sido creada con el objetivo de:

1. Demostrar cómo funcionan las vulnerabilidades web comunes
2. Proporcionar un entorno seguro para practicar el escaneo de vulnerabilidades
3. Enseñar la importancia de la seguridad en aplicaciones web
4. Servir como objetivo para probar herramientas de escaneo de seguridad

## Adaptación para Railway

Railway proporciona automáticamente una base de datos PostgreSQL y configura la variable de entorno `DATABASE_URL`. La aplicación está preparada para funcionar correctamente con esta configuración.

## Notas técnicas

- La aplicación utiliza SQLAlchemy como ORM para interactuar con PostgreSQL
- La vulnerabilidad de SQL Injection se mantiene usando consultas SQL directas a través de `db.session.execute()`
- La aplicación transforma automáticamente las URLs de conexión desde `postgres://` a `postgresql://` para compatibilidad con SQLAlchemy
- Los archivos `Procfile` y `railway.json` están configurados para el despliegue en Railway