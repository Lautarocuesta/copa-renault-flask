from flask import Flask, render_template

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

if __name__ == '__main__':
    app.run(debug=True)
