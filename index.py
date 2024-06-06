from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import random
import uuid

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///carrito.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Definición del modelo de base de datos
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    items = db.Column(db.String, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    order_number = db.Column(db.String(50), unique=True, nullable=False)

# Inicializar la base de datos dentro del contexto de la aplicación
with app.app_context():
    db.create_all()

# Lista de sponsors
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

app.secret_key = 'copa'

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
    items = ", ".join([f"{name} x{details['quantity']}" for name, details in cart.items()])

    order_number = generate_order_number()

    order = Order(items=items, total_price=total_price, order_number=order_number)
    db.session.add(order)
    db.session.commit()

    session.pop('cart', None)
    session.modified = True

    flash(f'Carrito enviado. Total: ${total_price:.2f} - Número de pedido: {order_number}')
    return redirect(url_for('carta'))

@app.route('/orders')
def orders():
    orders = Order.query.all()
    return render_template('orders.html', orders=orders)

def generate_order_number():
    return str(uuid.uuid4().hex)[:10]

if __name__ == '__main__':
    app.run(debug=True)
