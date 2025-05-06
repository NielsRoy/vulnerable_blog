from flask import Flask, render_template, request, redirect, session, url_for, make_response, flash
from flask_sqlalchemy import SQLAlchemy
import os
import re
from sqlalchemy.sql import text

app = Flask(__name__)
app.secret_key = "super_insecure_secret_key"  # Vulnerabilidad: Clave secreta débil

# Configuración de PostgreSQL
# URL de conexión para Railway: postgresql://postgres:password@containers-us-west-10.railway.app:5432/railway
# Para desarrollo local, ajusta según tu configuración
db_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/vulnerable_blog')
# Asegurarse de que la URL empiece con postgresql:// (Railway usa postgres://)
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Definición de modelos
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(50), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)

# Función para inicializar la base de datos
def init_db():
    with app.app_context():
        db.create_all()
        
        # Agregar usuario por defecto si no existe
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password='admin123')
            db.session.add(admin)
            db.session.commit()
        
        # Agregar algunos posts por defecto si no existen
        if Post.query.count() == 0:
            posts = [
                Post(title='Introducción a la Seguridad Web', 
                     content='La seguridad web es esencial para proteger datos sensibles. Las aplicaciones web modernas están expuestas a múltiples amenazas que pueden comprometer la integridad, confidencialidad y disponibilidad de los datos. Este blog explorará las vulnerabilidades más comunes y cómo mitigarlas.', 
                     author='admin'),
                Post(title='¿Qué es SQL Injection?', 
                     content='SQL Injection es una vulnerabilidad común que permite a un atacante insertar código SQL malicioso en consultas que la aplicación envía a la base de datos. Esto puede resultar en acceso no autorizado a datos sensibles, modificación de información e incluso control completo del servidor. Es una de las vulnerabilidades más peligrosas en aplicaciones web.', 
                     author='admin'),
                Post(title='Protección contra XSS', 
                     content='Cross-Site Scripting (XSS) es una vulnerabilidad donde los atacantes pueden inyectar scripts maliciosos que se ejecutan en el navegador de los usuarios. Existen tres tipos principales: Reflected XSS, Stored XSS y DOM-based XSS. Para protegerse, es fundamental validar todas las entradas de usuario y utilizar técnicas de escape de contenido adecuadas.', 
                     author='admin')
            ]
            for post in posts:
                db.session.add(post)
            db.session.commit()

# Rutas de la aplicación
@app.route('/')
def index():
    # Vulnerabilidad SQL Injection: uso de string format en consulta SQL
    query = "SELECT id, title, content, author FROM posts ORDER BY id DESC"
    result = db.session.execute(text(query))
    posts = result.fetchall()
    return render_template('index.html', posts=posts, username=session.get('username'))

@app.route('/search')
def search():
    q = request.args.get('q', '')
    
    # Vulnerabilidad SQL Injection: uso directo de parámetro en consulta SQL
    # Usando ILIKE en lugar de LIKE para búsquedas case-insensitive
    query = f"SELECT id, title, content, author FROM posts WHERE title ILIKE '%{q}%' OR content ILIKE '%{q}%'"
    result = db.session.execute(text(query))
    posts = result.fetchall()
    
    return render_template('search.html', posts=posts, query=q, username=session.get('username'))

@app.route('/post/<int:post_id>')
def view_post(post_id):
    # Vulnerabilidad SQL Injection: uso directo de parámetro en consulta SQL
    query = f"SELECT id, title, content, author FROM posts WHERE id = {post_id}"
    result = db.session.execute(text(query))
    post = result.fetchone()
    
    if not post:
        return redirect(url_for('index'))
    
    # Obtener comentarios
    comment_query = f"SELECT id, post_id, author, content FROM comments WHERE post_id = {post_id}"
    comment_result = db.session.execute(text(comment_query))
    comments = comment_result.fetchall()
    
    return render_template('post.html', post=post, comments=comments, username=session.get('username'))

@app.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    if not session.get('username'):
        return redirect(url_for('login'))
    
    comment_content = request.form.get('comment', '')
    
    # Vulnerabilidad XSS: no se sanitiza el contenido del comentario
    new_comment = Comment(
        post_id=post_id,
        author=session['username'],
        content=comment_content
    )
    
    db.session.add(new_comment)
    db.session.commit()
    
    return redirect(url_for('view_post', post_id=post_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Vulnerabilidad SQL Injection: uso directo de parámetros en consulta SQL
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        result = db.session.execute(text(query))
        user = result.fetchone()
        
        if user:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            error = 'Credenciales inválidas. Inténtalo de nuevo.'
    
    return render_template('login.html', error=error, username=session.get('username'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Verificar si el usuario ya existe
        existing_user = User.query.filter_by(username=username).first()
        
        if existing_user:
            error = 'El nombre de usuario ya está en uso. Elige otro.'
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            
            session['username'] = username
            return redirect(url_for('index'))
    
    return render_template('register.html', error=error, username=session.get('username'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not session.get('username'):
        return redirect(url_for('login'))
    
    # Vulnerabilidad CSRF: no hay token CSRF
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        
        # Actualizar contraseña
        user = User.query.filter_by(username=session['username']).first()
        if user:
            user.password = new_password
            db.session.commit()
            # Usando el patrón PRG (Post/Redirect/Get) para evitar reenvío de formulario
            # Almacenamos un mensaje de éxito en la sesión
            session['password_changed'] = True
            return redirect(url_for('profile'))
    
    # Recuperar y eliminar el mensaje de la sesión si existe
    password_changed = session.pop('password_changed', False)
    return render_template('profile.html', username=session.get('username'), password_changed=password_changed)

@app.route('/delete-account', methods=['POST'])
def delete_account():
    if not session.get('username'):
        return redirect(url_for('login'))

    # Vulnerabilidad CSRF: no hay token CSRF
    # Eliminar usuario
    user = User.query.filter_by(username=session['username']).first()
    if user:
        # Eliminar comentarios del usuario
        Comment.query.filter_by(author=session['username']).delete()
        
        # Eliminar posts del usuario
        Post.query.filter_by(author=session['username']).delete()
        
        # Eliminar usuario
        db.session.delete(user)
        db.session.commit()
        
        # Cerrar sesión
        session.pop('username', None)
        
        # Informar al usuario que la cuenta ha sido eliminada
        flash('Tu cuenta ha sido eliminada permanentemente', 'success')
        
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html', username=session.get('username'))

@app.route('/redirect')
def open_redirect():
    # Capturar la URL de redirección del parámetro
    url = request.args.get('url', '')
    
    if url:
        # En lugar de redirigir directamente, mostrar una página intermedia
        return render_template('redirect_warning.html', redirect_url=url)
    
    return redirect(url_for('index'))

@app.after_request
def add_header(response):
    # Vulnerabilidad de Headers: no se agregan headers de seguridad importantes
    # No se agrega X-Frame-Options (Clickjacking)
    # No se agrega Content-Security-Policy
    # No se agrega X-Content-Type-Options
    # No se agrega X-XSS-Protection
    return response

# Inicializar la base de datos al arrancar la aplicación
init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)