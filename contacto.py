from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, TextAreaField, EmailField, SelectField
from wtforms.validators import DataRequired, Email, Length

# Definir un Blueprint para la sección de contacto
contacto_bp = Blueprint('contacto', __name__)

# Definir el formulario de contacto
class ContactForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired()])
    school = StringField('Colegio', validators=[DataRequired()])
    email = EmailField('Correo Electrónico', validators=[DataRequired(), Email()])
    roles = SelectField('Rol', choices=[('Profesor', 'Profesor'), ('Jugador', 'Jugador'), ('Técnico', 'Técnico'), ('Otro', 'Otro')], validators=[DataRequired()])
    other_role = StringField('Especifique su rol (si eligió "Otro")')
    age = IntegerField('Edad', validators=[DataRequired()])
    message = TextAreaField('Mensaje', validators=[DataRequired()])
    submit = SubmitField('Enviar')

# Ruta para mostrar el formulario de contacto
@contacto_bp.route('/contacto', methods=['GET', 'POST'])
def contacto():
    form = ContactForm()
    if form.validate_on_submit():
        # Procesar el formulario
        flash(f"Formulario enviado por {form.name.data} desde {form.school.data}")
        return redirect(url_for('contacto.contacto'))
    return render_template('contacto.html', form=form)

