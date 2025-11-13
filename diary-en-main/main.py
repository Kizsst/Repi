# Importación
from flask import Flask, render_template, request, redirect, session
# Conexión de la biblioteca de bases de datos
from flask_sqlalchemy import SQLAlchemy
import os 

app = Flask(__name__)
# Establecer la clave secreta para la sesión.
app.secret_key = 'my_top_secret_123'
# Estableciendo conexión SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Creando la DB
db = SQLAlchemy(app)

# Tarea #1. Crear la tabla de usuarios
class User(db.Model):
    # Creating the columns
    # id
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Cambiado a 'email' para coincidir con el campo del formulario y la lógica de la tarjeta
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'<User {self.id}>'


# Creando la tabla de tarjetas
class Card(db.Model):
    # Estableciendo los campos de enrada
    # id
    id = db.Column(db.Integer, primary_key=True)
    # título
    title = db.Column(db.String(100), nullable=False)
    # Descripción
    subtitle = db.Column(db.String(300), nullable=False)
    # Texto
    text = db.Column(db.Text, nullable=False)
    # El correo electrónico del propietario de la tarjeta.
    user_email = db.Column(db.String(100), nullable=False)

    # Objeto de salida y su ID
    def __repr__(self):
        return f'<Card {self.id}>'
    

# Lanzamiento de la página de contenido (Login)
@app.route('/', methods=['GET','POST'])
def login():
    # Verificar si el usuario ya tiene una sesión iniciada usando la clave estandarizada
    if 'user_email' in session:
        return redirect('/index')
        
    error = ''
    if request.method == 'POST':
        form_email = request.form['email']
        form_password = request.form['password']
            
        # Tarea #4. Implementar la verificación de usuario
        # Buscar el usuario por email
        user = User.query.filter_by(email=form_email).first()

        # Verificar si el usuario existe y si la contraseña coincide
        if user and user.password == form_password:
            # Si el inicio de sesión es exitoso, guardar el email del usuario en la sesión
            session['user_email'] = user.email
            return redirect('/index')
        else:
            # Si falla, mostrar mensaje de error
            error = 'Login o contraseña incorrectos'
            return render_template('login.html', error=error)

    # Mostrar el formulario de login en la solicitud GET
    return render_template('login.html')


@app.route('/reg', methods=['GET','POST'])
def reg():
    if request.method == 'POST':
        email = request.form['email'] # El campo de formulario se llama 'email'
        password = request.form['password']
        
        # Tarea #3. Implementar grabación de usuarios
        try:
            user = User(email=email, password=password) # Usar el campo 'email' de la DB
            db.session.add(user)
            db.session.commit()
            return redirect('/')
        except:
            # Manejar el caso de que el email ya exista (unique=True)
            error = 'Este correo ya está registrado.'
            return render_template('registration.html', error=error)
    
    else:
        return render_template('registration.html')

@app.route('/logout')
def logout():
    # Eliminar la clave de sesión estandarizada
    session.pop('user_email', None)
    return redirect('/')


# Iniciar página de contenido (Index)
@app.route('/index')
def index():
    # Asegurar que el usuario esté logueado
    if 'user_email' not in session:
        return redirect('/')

    # Tarea # 4. Asegúrese de que el usuario solo vea sus propias tarjetas
    email = session.get('user_email')
    # Filtrar tarjetas solo para el usuario logueado
    cards = Card.query.filter_by(user_email=email).all()

    # Retornar el template con las tarjetas
    return render_template('index.html', cards=cards)


# Lanzando la página de la tarjeta
@app.route('/card/<int:id>')
def card(id):
    # Asegurar que el usuario esté logueado
    if 'user_email' not in session:
        return redirect('/')

    # Obtener el email del usuario de la sesión
    user_email = session['user_email']
    # Filtrar la tarjeta por ID Y por email del usuario para seguridad
    card = Card.query.filter_by(id=id, user_email=user_email).first()
    
    if not card:
        return redirect('/index')

    return render_template('card.html', card=card)

# Iniciando la página de creación de tarjetas
@app.route('/create')
def create():
    # Asegurar que el usuario esté logueado
    if 'user_email' not in session:
        return redirect('/')
        
    return render_template('create_card.html')

# la forma de la tarjeta (Procesamiento del formulario de creación)
@app.route('/form_create', methods=['GET','POST'])
def form_create():
    # Asegurar que el usuario esté logueado
    if 'user_email' not in session:
        return redirect('/')
        
    if request.method == 'POST':
        title = request.form['title']
        subtitle = request.form['subtitle']
        text = request.form['text']
        
        # Tarea # 4. Hacer que la creación de la tarjeta se realice en nombre del usuario
        # Obtener el email del usuario de la sesión
        user_email = session['user_email']
        card = Card(title=title, subtitle=subtitle, text=text, user_email=user_email)

        db.session.add(card)
        db.session.commit()
        return redirect('/index')
    else:
        # Esto es solo si alguien accede a /form_create con GET (aunque la ruta es POST)
        return redirect('/create')

if __name__ == "__main__":
    # Asegurarse de que la base de datos se crea dentro del contexto de la aplicación
    with app.app_context():
        # Crear todas las tablas si no existen
        db.create_all()

        # Lógica para crear un usuario de prueba si la tabla está vacía
        if not User.query.first():
            # Creamos el usuario por defecto: admin@diario.com con contraseña 12345
            admin_user = User(email='admin@diario.com', password='12345')
            db.session.add(admin_user)
            db.session.commit()
            print("--- Usuario 'admin@diario.com' creado automáticamente para pruebas. ---")
            
    # Ejecutar la aplicación
    app.run(debug=True)
