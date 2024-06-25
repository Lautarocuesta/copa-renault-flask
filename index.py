from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
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
        'connect_timeout': 60  # Aumentar el tiempo de espera a 60 segundos
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
    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    payment_method_id = db.Column(db.Integer, db.ForeignKey('PaymentMethods.payment_method_id'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    order_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    status_id = db.Column(db.Integer, db.ForeignKey('OrderStatus.status_id'), nullable=False)
    order_number = db.Column(db.String(10), unique=True, nullable=False)  # Agregar este campo para el número de orden

    def __repr__(self):
        return f'<Order {self.order_id}>'

class OrderDetail(db.Model):
    __tablename__ = 'OrderDetails'
    order_detail_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('Orders.order_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('Products.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

class Notification(db.Model):
    __tablename__ = 'Notifications'
    notification_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('Orders.order_id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    sent_date = db.Column(db.DateTime, default=db.func.current_timestamp())

# Create all necessary tables
with app.app_context():
    try:
        db.create_all()
        print("La base de datos se ha creado correctamente.")
    except OperationalError as e:
        print("Error al conectar con la base de datos:", e)
    except Exception as e:
        print("Error:", e)

# List of sponsors
sponsors = [
    "beltran", "city", "congreso", "fie", "grido", 
    "image", "khalama", "patagonia", "pretty", "principito", 
    "pritty", "s20", 
]

@app.route('/')
def home():
    return render_template('home.html', sponsors=sponsors)

@app.route('/contacto')
def contacto():
    nombres = ["Cuesta", "Carnalito", "Pajan"]
    return render_template("contacto.html", nombres=nombres)

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
    return render_template('carta.html', menu_items=menu_items, cart=session.get('cart', {}))

menu_items = [
    {'name': 'Hamburguesa', 'price': 5.99},
    {'name': 'Pizza', 'price': 8.99},
    {'name': 'Ensalada', 'price': 4.99},
    {'name': 'Soda', 'price': 1.99},
    {'name': 'Agua', 'price': 0.99},
]

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

    with app.app_context():
        try:
            # Crear la instancia de Order
            order = Order(user_id=user_id,
                          payment_method_id=payment_method_id,
                          total_amount=total_price,
                          order_number=order_number,
                          status_id=status_id)
            db.session.add(order)
            db.session.commit()

            # Ahora que la orden se ha guardado correctamente, 
            # podemos proceder a guardar los detalles de la orden
            for item_name, details in cart.items():
                product = Product.query.filter_by(name=item_name).first()
                order_detail = OrderDetail(order_id=order.order_id,
                                           product_id=product.product_id,
                                           quantity=details['quantity'],
                                           price=details['price'])
                db.session.add(order_detail)
            
            db.session.commit()

            session.pop('cart', None)
            session.modified = True

            flash(f'Carrito enviado. Total: ${total_price:.2f} - Número de pedido: {order_number}')
            return redirect(url_for('carta'))

        except Exception as e:
            db.session.rollback()
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

if __name__ == '__main__':
    app.run(debug=True)
