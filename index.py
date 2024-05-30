from flask import Flask, render_template, request, redirect, url_for, session  # Importa también 'request'

import random


app = Flask(__name__)

# Lista de sponsors de ejemplo
sponsors = ["Nike", "Adidas", "Coca-Cola", "Pepsi", "Visa", "Apple", "Samsung"]

@app.route('/')
def home():
    return render_template('home.html',sponsors=sponsors)

@app.route('/contacto')
def contacto():
    nombres = ["Cuesta", "Carnalito", "Pajan"]
    return render_template("contacto.html", nombres=nombres)

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    # Aquí procesas los datos del formulario
    nombre = request.form['nombre']
    return f'Formulario enviado por {nombre}'

@app.route('/sponsors')  # Ruta para mostrar los sponsors aleatorios
def sponsors_random():
    # Mezclar los sponsors en orden aleatorio
    random.shuffle(sponsors)
    return render_template("spo.html", sponsors=sponsors)
    
@app.route('/carta')
def carta():
    if 'cart' not in session:
        session['cart'] = []
    return render_template('carta.html', menu_items=menu_items, cart=session['cart'])

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
        session['cart'] = []
    session['cart'].append(item_name)
    session.modified = True
    return redirect(url_for('carta'))

if __name__ == '__main__':
    app.run(debug=True)
