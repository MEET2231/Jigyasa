from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)
app.secret_key = 'secret_key'

# Database connection
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'MMGM',
    'database': 'form_builder'
}

def db_connection():
    return mysql.connector.connect(**db_config)

# Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Create Form
@app.route('/create_form', methods=['GET', 'POST'])
def create_form():
    if request.method == 'POST':
        form_name = request.form['form_name']
        fields = request.form.getlist('fields')
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO forms (name) VALUES (%s)", (form_name,))
        form_id = cursor.lastrowid
        for field in fields:
            cursor.execute("INSERT INTO fields (form_id, field_name) VALUES (%s, %s)", (form_id, field))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('view_forms'))
    return render_template('create_form.html')

# View Forms
@app.route('/view_forms')
def view_forms():
    conn = db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM forms")
    forms = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('view_forms.html', forms=forms)

# Fill Form
@app.route('/fill_form/<int:form_id>', methods=['GET', 'POST'])
def fill_form(form_id):
    conn = db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM fields WHERE form_id = %s", (form_id,))
    fields = cursor.fetchall()
    cursor.close()
    if request.method == 'POST':
        responses = [(form_id, field['field_name'], request.form[field['field_name']]) for field in fields]
        cursor = conn.cursor()
        for response in responses:
            cursor.execute("INSERT INTO responses (form_id, field_name, response) VALUES (%s, %s, %s)", response)
        conn.commit()
        cursor.close()
        conn.close()
        return render_template('success.html')
    return render_template('fill_form.html', fields=fields)

if __name__ == '__main__':
    app.run(debug=True)
