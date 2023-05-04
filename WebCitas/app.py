from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from flask_mysqldb import MySQL
import pdfkit
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'nombre_de_tu_base_de_datos'
mysql = MySQL(app)

app.secret_key = "mysecretkey"



def get_paciente_by_id(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM pacientes WHERE id_p = %s", (id,))
    registro = cursor.fetchone()
    return registro


@app.route('/pacientes/delete/<int:id>', methods=['POST'])
def delete_paciente(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM pacientes WHERE id_p = %s', (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('pacientes'))


@app.route('/registro.html')
def registro():
    return render_template("registro.html")


@app.route('/agregar_medicos', methods=['GET', 'POST'])
def agregar_medicos():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido_paterno = request.form['apellido_paterno']
        apellido_materno = request.form['apellido_materno']
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        telefono = request.form['telefono']
        especialidad = request.form['especialidad']
        codigo_postal = request.form['codigo_postal']

        cur = mysql.connection.cursor()  
        cur.execute("INSERT INTO medicos (nombre, apellido_paterno, apellido_materno, correo, contraseña, telefono, especialidad, codigo_postal) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (nombre, apellido_paterno, apellido_materno, correo, contraseña, telefono, especialidad, codigo_postal))
        mysql.connection.commit()
        cur.close()  
        flash("Registro Completo!")
        return redirect(url_for("login"))
    return render_template('agregar_medicos.html')



@app.route('/add.html', methods=['POST'])
def add():
    if request.method == "POST":
        nombres = request.form["nombres"]
        apellido_pat = request.form["apellido_paterno"]
        apellido_mat = request.form["apellido_materno"]
        correo = request.form["correo"]
        password = request.form["contraseña"]
        telefono = request.form["telefono"]
        edad = request.form["edad"]
        tipo_sangre = request.form["tipo_sangre"]
        peso = request.form["peso"]
        estatura = request.form["estatura"]
        codigo_postal = request.form["codigo_postal"]
        cur = mysql.connection.cursor()
        
        
        cur.execute("SELECT correo FROM pacientes WHERE correo=%s", (correo,))
        result = cur.fetchone()
        if result:
            flash("Correo registrado.")
            return redirect(url_for("registro"))

        
        cur.execute("INSERT INTO pacientes (nombres, apellido_paterno, apellido_materno, correo, contraseña, telefono, edad, tipo_sangre, peso, estatura, codigo_postal) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (nombres, apellido_pat, apellido_mat, correo, password, telefono, edad, tipo_sangre, peso, estatura, codigo_postal))
        mysql.connection.commit()
        flash("Registro Completo!")
        return redirect(url_for("login"))



@app.route('/')
def index():
    return render_template("index.html")




@app.route('/Especialidades.html')
def specialties():
    return render_template("Especialidades.html")



@app.route('/sacar_citas', methods=['GET', 'POST'])
def sacar_citas():
    if request.method == 'POST':
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        correo = request.form['correo']
        sintomas = request.form['sintomas']
        fecha = request.form['fecha']
        hora = request.form['hora']
        medico_id = request.form['medico']

        cur = mysql.connection.cursor()
        cur.execute("SELECT id_c, fecha, hora, medico FROM citas WHERE nombre = %s", [nombre])
        cita_existente = cur.fetchone()

        if cita_existente:
            flash(f"Ya tienes una cita programada para el {cita_existente[1]} a las {cita_existente[2]} con el médico {cita_existente[3]}")
            return redirect(url_for("sacar_citas"))

        cur = mysql.connection.cursor()
        cur.execute("SELECT nombre, especialidad, correo FROM medicos WHERE id_m=%s", [medico_id])
        medico = cur.fetchone()

        cur.execute("INSERT INTO citas (nombre, telefono, correo, sintomas, fecha, hora, medico) VALUES (%s, %s, %s, %s, %s, %s, %s)", (nombre, telefono, correo, sintomas, fecha, hora, medico[0]))
        mysql.connection.commit()

        cur.close()

        msg = MIMEMultipart()
        msg['From'] = 'lgpacual@gmail.com'
        msg['To'] = correo
        msg['Subject'] = 'Confirmación de cita médica'
        message = f'Hola {nombre},\n\nTu cita ha sido registrada exitosamente para el día {fecha} a las {hora} con el médico {medico[0]} ({medico[1]}).\n\nAtentamente,\nTu clínica'
        msg.attach(MIMEText(message))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('lgpacual@gmail.com', 'oqsxfjmmrujfuthq')
        text = msg.as_string()
        server.sendmail('lgpacual@gmail.com', correo, text)
        server.quit()

        flash('Cita registrada correctamente')
        return redirect(url_for("dashboard"))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id_m, nombre, especialidad FROM medicos")
    medicos = cur.fetchall()
    cur.close()
    return render_template("sacar_citas.html", medicos=medicos)



@app.route('/lista_citas')
def lista_citas():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM citas")
    citas = cur.fetchall()
    cur.close()

    return render_template("lista_citas.html", citas=citas)


@app.route('/citas/delete/<int:id>', methods=['POST', 'DELETE'])
def delete_cita(id):
    if request.method == 'POST' or request.method == 'DELETE':
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM citas WHERE id_c = %s', (id,))
        mysql.connection.commit()
        cur.close()
        flash('Cita eliminada exitosamente', 'success')
        return redirect(url_for('lista_citas'))




@app.route('/Medicos')
def Medicos():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM nombre_de_tu_base_de_datos.medicos')
    medicos = cur.fetchall()
    cur.close()
    return render_template('Medicos.html', medicos=medicos)  

    
@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        cur = mysql.connection.cursor()

        cur.execute("SELECT * FROM pacientes WHERE correo=%s AND contraseña=%s", (correo, contraseña))
        paciente = cur.fetchone()

        if not paciente:
            cur.execute("SELECT * FROM medicos WHERE correo=%s AND contraseña=%s", (correo, contraseña))
            medico = cur.fetchone()

            if medico:
                session['loggedin'] = True
                session['correo'] = correo
                session['nombres'] = medico[1]
                session['apellidos'] = medico[2]
                session['especialidad'] = medico[6]
                session['tipo_usuario'] = 'medico'
                return redirect(url_for('dashboard'))

        elif paciente:
            session['loggedin'] = True
            session['correo'] = correo
            session['nombres'] = paciente[1]
            session['apellidos'] = paciente[2]
            session['tipo_usuario'] = 'paciente'
            return redirect(url_for('dashboard'))

        flash('Correo o contraseña incorrectos.')

    return render_template("login.html")



@app.route('/generate_pdf/<int:id>', methods=['POST'])
def generate_pdf(id):
    
    paciente = get_paciente_by_id(id)

    
    html = render_template('datos_paciente.html', paciente=paciente)

    
    pdf = pdfkit.from_string(html, False)

   
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=paciente_{id}.pdf'

    return response



@app.route('/pacientes')
def pacientes():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM nombre_de_tu_base_de_datos.pacientes')
    registros = cur.fetchall()
    cur.close()
    return render_template('lista_pacientes.html', registros=registros)



@app.route('/pacientes/edit/<int:id>', methods=['GET', 'POST'])
def edit_paciente(id):
    registro = get_paciente_by_id(id)
    if request.method == 'POST':
        nombres = request.form['nombres']
        apellido_paterno = request.form['apellido_paterno']
        apellido_materno = request.form['apellido_materno']
        correo = request.form['correo']
        telefono = request.form['telefono']
        edad = request.form['edad']
        tipo_sangre = request.form['tipo_sangre']
        peso = request.form['peso']
        estatura = request.form['estatura']
        codigo_postal = request.form['codigo_postal']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE pacientes SET nombres = %s, apellido_paterno = %s, apellido_materno = %s, correo = %s, telefono = %s, edad = %s, tipo_sangre = %s, peso = %s, estatura = %s, codigo_postal = %s WHERE id_p = %s",
        (nombres, apellido_paterno, apellido_materno, correo, telefono, edad, tipo_sangre, peso, estatura, codigo_postal, id))
        mysql.connection.commit()
        cur.close()
        flash('Registro exitoso!')
        return redirect(url_for('pacientes'))
    return render_template('edit_paciente.html', registro=registro)



@app.route('/dashboard.html')
def dashboard():
    if 'loggedin' in session:
        correo = session['correo']
        nombres = session['nombres']
        apellidos = session['apellidos']

        
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM pacientes"
        cursor.execute(query)
        pacientes = cursor.fetchall()
        cursor.close()

        return render_template('dashboard.html', correo=correo, nombres=nombres, apellidos=apellidos, pacientes=pacientes)
    return redirect(url_for('login'))


@app.route('/logout.html', methods= ["GET","POST"])
def logout():
    session.pop('correo', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port= 8000)

