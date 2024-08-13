from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateTimeField, IntegerField, TextAreaField, EmailField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length
from datetime import datetime, timedelta
from contacto import contacto_bp
from contacto import ContactForm
import random
import uuid
import pymysql
import logging

# Configure logging for SQLAlchemy
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
logging.getLogger('pymysql').setLevel(logging.DEBUG)

# Install pymysql as MySQLdb
pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.secret_key = 'copa'

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://uezytq7dxx48hp8w:s18HO1qr2Nw46fXbuHPg@bhyb1fa898t0ow9ufdlc-mysql.services.clever-cloud.com/bhyb1fa898t0ow9ufdlc'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {
        'connect_timeout': 60  # Increase the timeout to 60 seconds
    }
}

# Initialize SQLAlchemy
db = SQLAlchemy(app)


# Define SQLAlchemy Models
class User(db.Model):
    __tablename__ = 'Users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'


class Product(db.Model):
    __tablename__ = 'Products'
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)


class PaymentMethod(db.Model):
    __tablename__ = 'PaymentMethods'
    payment_method_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    method_name = db.Column(db.String(50), nullable=False)


class OrderStatus(db.Model):
    __tablename__ = 'OrderStatus'
    status_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status_name = db.Column(db.String(50), nullable=False)


class Order(db.Model):
    __tablename__ = 'Orders'

    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'))
    payment_method_id = db.Column(db.Integer, db.ForeignKey('PaymentMethods.payment_method_id'))
    total_amount = db.Column(db.Float)
    order_date = db.Column(db.DateTime, default=datetime.now)
    status_id = db.Column(db.Integer, db.ForeignKey('OrderStatus.status_id'))
    order_number = db.Column(db.String(50), unique=True)

    def __repr__(self):
        return f'<Order {self.order_id}>'


class OrderDetail(db.Model):
    __tablename__ = 'OrderDetails'
    order_detail_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('Orders.order_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('Products.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

class ContactForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired()])
    school = StringField('Colegio', validators=[DataRequired()])
    email = EmailField('Correo Electrónico', validators=[DataRequired(), Email()])
    roles = SelectField('Rol', choices=[('Profesor', 'Profesor'), ('Jugador', 'Jugador'), ('Técnico', 'Técnico'), ('Otro', 'Otro')], validators=[DataRequired()])
    other_role = StringField('Especifique su rol (si eligió "Otro")')
    age = IntegerField('Edad', validators=[DataRequired()])
    message = TextAreaField('Mensaje', validators=[DataRequired()])
    submit = SubmitField('Enviar')

class Division(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class Stage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sport = db.Column(db.String(50), nullable=False)
    stage = db.Column(db.String(20), nullable=False)  # 16th, 8th, etc.
    division = db.Column(db.String(20), nullable=False)  # minor, intermediate, major
    team1 = db.Column(db.String(100), nullable=False)
    team2 = db.Column(db.String(100), nullable=False)
    score_team1 = db.Column(db.Integer, nullable=True)
    score_team2 = db.Column(db.Integer, nullable=True)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    winner = db.Column(db.String(100), nullable=True)

class MatchForm(FlaskForm):
    sport = StringField('Sport', validators=[DataRequired()])
    stage = SelectField('Stage', choices=[('16th', '16th'), ('8th', '8th'), ('Quarterfinal', 'Quarterfinal'), ('Semifinal', 'Semifinal'), ('Final', 'Final')], validators=[DataRequired()])
    division = SelectField('Division', choices=[('minor', 'Minor'), ('intermediate', 'Intermediate'), ('major', 'Major')], validators=[DataRequired()])
    team1 = StringField('Team 1', validators=[DataRequired()])
    team2 = StringField('Team 2', validators=[DataRequired()])
    date = DateTimeField('Match Date', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    submit = SubmitField('Add Match')

class Notification(db.Model):
    __tablename__ = 'Notifications'
    notification_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('Orders.order_id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    sent_date = db.Column(db.DateTime, default=db.func.current_timestamp())


# Function to add the 'order_number' column if it does not exist
def add_order_number_column():
    try:
        with app.app_context():
            # Intenta añadir la columna si no existe
            if not hasattr(Order, 'order_number'):
                db.session.execute('ALTER TABLE Orders ADD COLUMN order_number VARCHAR(50)')
                db.session.commit()
    except OperationalError as e:
        print(f"Error adding column: {e}")

add_order_number_column()



# Create all necessary tables
with app.app_context():
    try:
        db.create_all()
        add_order_number_column()
        print("La base de datos se ha creado correctamente.")
    except OperationalError as e:
        print("Error al conectar con la base de datos:", e)
    except Exception as e:
        print("Error:", e)


# List of sponsors
sponsors = [
    "beltran", "city", "congreso", "fie", "grido",
    "image", "khalama", "patagonia", "pretty", "principito",
    "pritty", "s10",
]


@app.route('/')
def home():
    return render_template('home.html', sponsors=sponsors)


@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    form = ContactForm()
    if form.validate_on_submit():
        # Procesar el formulario
        flash(f"Formulario enviado por {form.name.data} desde {form.school.data}")
        return redirect(url_for('contacto'))
    return render_template('contacto.html', form=form)

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    nombre = request.form['nombre']
    return f'Formulario enviado por {nombre}'


@app.route('/sponsors')
def sponsors_random():
    random.shuffle(sponsors)
    return render_template("spo.html", sponsors=sponsors)


@app.route('/carta')
def carta():
    currency = session.get('currency', 'ARS')
    exchange_rate = 1385 if currency == 'ARS' else 1  # Example exchange rate: 1 ARS = 0.005 USD
    menu_items_converted = []

    for item in menu_items:
        price_converted = item['price'] * exchange_rate
        menu_items_converted.append({
            "name": item['name'],
            "price": item['price'],
            "price_converted": price_converted,
            "image": item['image']
        })

    cart_converted = {name: {'price': details['price'] * exchange_rate, 'quantity': details['quantity']}
                      for name, details in session.get('cart', {}).items()}

    

    return render_template('carta.html', menu_items=menu_items_converted, cart=cart_converted, currency=currency)



menu_items = [
    {"name": "Agua", "price": 1.00, "image": "agua.png"},
    {"name": "Coca", "price": 1.50, "image": "coca.png"},
    {"name": "Ensalada", "price": 3.00, "image": "ensalada.png"},
    {"name": "Hamburguesa", "price": 8.00, "image": "hambur.png"},
    {"name": "Pizza", "price": 8.00, "image": "pizza.png"},
]
@app.route('/change_currency', methods=['POST'])
def change_currency():
    currency = request.form['currency']
    session['currency'] = currency
    return redirect(url_for('carta'))


@app.route('/add_to_cart/<item_name>')
def add_to_cart(item_name):
    if 'cart' not in session:
        session['cart'] = {}
    cart = session['cart']
    if item_name in cart:
        cart[item_name]['quantity'] += 1
    else:
        for item in menu_items:
            if item['name'] == item_name:
                cart[item_name] = {'price': item['price'], 'quantity': 1}
                break
    session.modified = True
    return redirect(url_for('carta'))


@app.route('/update_cart/<item_name>/<action>')
def update_cart(item_name, action):
    if 'cart' in session and item_name in session['cart']:
        if action == 'increment':
            session['cart'][item_name]['quantity'] += 1
        elif action == 'decrement' and session['cart'][item_name]['quantity'] > 1:
            session['cart'][item_name]['quantity'] -= 1
        elif action == 'decrement' and session['cart'][item_name]['quantity'] == 1:
            session['cart'].pop(item_name)
        session.modified = True
    return redirect(url_for('carta'))


@app.route('/send_cart', methods=['POST'])
def send_cart():
    cart = session.get('cart', {})
    total_price = sum(item['price'] * item['quantity'] for item in cart.values())

    order_number = generate_order_number()

    user_id = 1  # Aquí debes establecer el usuario correcto
    payment_method_id = 1  # Aquí debes establecer el método de pago correcto
    status_id = 1  # Aquí debes establecer el estado correcto de la orden

    # Establecer el tiempo actual y calcular la hora de entrega estimada
    order_date = datetime.now()
    estimated_delivery_time = order_date + timedelta(minutes=30)

    with app.app_context():
        try:
            # Crear la instancia de Order
            order = Order(user_id=user_id,
                          payment_method_id=payment_method_id,
                          total_amount=total_price,
                          order_number=order_number,
                          status_id=status_id,
                          order_date=order_date)
            db.session.add(order)
            db.session.commit()

            # Guardar los detalles de la orden
            for item_name, details in cart.items():
                product = Product.query.filter_by(name=item_name).first()
                if product is None:
                    flash(f'Error: Producto {item_name} no encontrado.')
                    return redirect(url_for('carta'))
                order_detail = OrderDetail(order_id=order.order_id,
                                           product_id=product.product_id,
                                           quantity=details['quantity'],
                                           price=details['price'])
                db.session.add(order_detail)

            db.session.commit()

            session.pop('cart', None)
            session.modified = True

            flash(f'Carrito enviado. Total: ${total_price:.2f} - Número de pedido: {order_number}. Tiempo estimado de entrega: {estimated_delivery_time.strftime("%H:%M:%S")}')
            return redirect(url_for('carta'))

        except Exception as e:
            db.session.rollback()
            logging.error(f'Error al procesar la orden: {e}')
            flash('Error al procesar la orden. Por favor, inténtelo de nuevo más tarde.')
            return redirect(url_for('carta'))

@app.route('/orders')
def orders():
    orders = Order.query.all()
    return render_template('orders.html', orders=orders)


def generate_order_number():
    return str(uuid.uuid4().hex)[:10]


@app.route('/ubicacion')
def ubicacion():
    return render_template('ubicacion.html')

@app.route('/add_match', methods=['GET', 'POST'])
def add_match():
    form = MatchForm()
    if form.validate_on_submit():
        new_match = Match(
            sport=form.sport.data,
            stage=form.stage.data,
            division=form.division.data,
            team1=form.team1.data,
            team2=form.team2.data,
            date=form.date.data,
            location=form.location.data,
        )
        db.session.add(new_match)
        db.session.commit()
        flash('Match added successfully', 'success')
        return redirect(url_for('index'))
    return render_template('add_match.html', form=form)

@app.route('/matches')
def view_matches():
    matches = Match.query.all()
    return render_template('matches.html', matches=matches) 


if __name__ == '__main__':
    app.run(debug=True)
