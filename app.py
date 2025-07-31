from flask import Flask, render_template, request, redirect, send_from_directory, url_for, session
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'votre_clef_secrete'
UPLOAD_FOLDER = 'static/uploads'
DATA_FILE = '/data/factures.json'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        fichier = request.files['fichier']
        if fichier:
            nom = request.form['nom']
            email = request.form['email']
            numero = request.form['numero']
            montant = request.form['montant']
            date_facture = request.form['date_facture']
            now = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = now + "_" + secure_filename(fichier.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            fichier.save(filepath)

            data = load_data()
            data.append({
                'date_envoi': now,
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
            return render_template('index.html', message="Votre facture a bien été envoyée.")
    return render_template('index.html')

@app.route('/download/<filename>')
def download_facture(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'motdepasse':
            session['admin'] = True
            return redirect('/admin')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/login')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin'):
        return redirect('/login')

    data = load_data()

    if request.method == 'POST':
        index = int(request.form['index'])
        action = request.form['action']

        if action == 'update':
            data[index]['statut'] = request.form['statut']
            data[index]['commentaire'] = request.form['commentaire']
        elif action == 'delete':
            fichier = data[index]['fichier']
            try:
                os.remove(os.path.join(UPLOAD_FOLDER, fichier))
            except:
                pass
            data.pop(index)
        save_data(data)
        return redirect('/admin')

    return render_template('admin.html', factures=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
