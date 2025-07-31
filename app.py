
import os
import json
from flask import send_file, Flask, render_template, request, redirect, url_for, send_from_directory, session
from datetime import datetime
from werkzeug.utils import secure_filename
import smtplib
from email.message import EmailMessage

DATA_FILE = "/data/data.json"
UPLOAD_FOLDER = "/data/uploads"

app = Flask(__name__)
app.secret_key = 'factures_secret_key'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ADMIN_LOGIN = 'integralesecuriteformations@gmail.com'
ADMIN_PASSWORD = 'Lv15052025@@'

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

def load_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def send_mail(nom, email, filename):
    msg = EmailMessage()
    msg['Subject'] = 'Nouvelle facture déposée'
    msg['From'] = 'ecole@integraleacademy.com'
    msg['To'] = 'ecole@integraleacademy.com'
    msg.set_content("Une nouvelle facture a été déposée par {} ({}). Fichier : {}".format(nom, email, filename))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login('ecole@integraleacademy.com', os.environ.get('EMAIL_PASSWORD'))
            smtp.send_message(msg)
    except Exception as e:
        print("Erreur envoi mail :", e)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nom = request.form['nom']
        email = request.form['email']
        numero = request.form['numero']
        montant = request.form['montant']
        date_facture = request.form['date']
        fichier = request.files['fichier']

        if fichier:
            filename = datetime.now().strftime("%Y%m%d%H%M%S_") + secure_filename(fichier.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            fichier.save(filepath)

            data = load_data()
            data.append({
                'date_envoi': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'nom': nom,
                'email': email,
                'numero': numero,
                'montant': montant,
                'date_facture': date_facture,
                'fichier': filename,
                'statut': 'En attente',
                'commentaire': ''
            })
            save_data(data)
            send_mail(nom, email, filename)
            return render_template('confirmation.html')

    return render_template('index.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    data = load_data()

    if request.method == 'POST':
        action = request.form.get('action')
        fichier_recu = request.form.get('fichier')
        data_modifiee = []

        for facture in data:
            if facture['fichier'] == fichier_recu:
                if action == 'delete':
                    try:
                        os.remove(os.path.join(UPLOAD_FOLDER, facture['fichier']))
                    except:
                        pass
                    continue
                else:
                    facture['statut'] = request.form.get('statut')
                    facture['commentaire'] = request.form.get('commentaire')
            data_modifiee.append(facture)

        save_data(data_modifiee)
        data = data_modifiee

    return render_template('admin.html', factures=data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['login'] == ADMIN_LOGIN and request.form['password'] == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/download/<filename>')
def download_facture(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
