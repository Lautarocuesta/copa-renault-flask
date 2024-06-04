from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

# Configuración de la base de datosssss
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///carrito.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Definición del modelo de base de datos
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    items = db.Column(db.String, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

# Inicializar la base de datos dentro del contexto de la aplicación
with app.app_context():
    db.create_all()

# Lista de sponsors de ejemplo
sponsors = ["Nike", "Adidas", "Coca-Cola", "Pepsi", "Visa", "Apple", "Samsung"]

@app.route('/')
def home():
    return render_template('home.html', sponsors=sponsors)

@app.route('/contacto')
def contacto():
    nombres = ["Cuesta", "Carnalito", "Pajan"]
    return render_template("contacto.html", nombres=nombres)

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    # Aquí procesas los datos del formulario
    nombre = request.form['nombre']
    return f'Formulario enviado por {nombre}'

@app.route('/sponsors')
def sponsors_random():
    # Mezclar los sponsors en orden aleatorio
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

    # Guardar el pedido en la base de datos
    order = Order(items=items, total_price=total_price)
    db.session.add(order)
    db.session.commit()

    # Limpiar el carrito
    session.pop('cart', None)
    session.modified = True

    flash(f'Carrito enviado. Total: ${total_price:.2f}')
    return redirect(url_for('carta'))

@app.route('/orders')
def orders():
    orders = Order.query.all()
    return render_template('orders.html', orders=orders)

if __name__ == '__main__':
    app.run(debug=True)
