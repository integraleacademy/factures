from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'votre_clé_secrète'

UPLOAD_FOLDER = 'static/factures'
ADMIN_LOGIN = 'admin'
ADMIN_PASSWORD = 'admin'

# --- Fonctions de lecture/écriture ---
def load_data():
    if not os.path.exists('data.json'):
        return []
    with open('data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- Routes publiques ---
@app.route('/')
def index():
    return render_template('index.html')

# --- Authentification ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == ADMIN_LOGIN and request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            error = 'Identifiants incorrects'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

# --- Tableau admin ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))

    data = load_data()

    # Traitement du POST (changement de statut ou suppression)
    if request.method == 'POST':
        action = request.form.get('action')
        index_str = request.form.get('index')

        if index_str is not None and index_str.isdigit():
            index = int(index_str)
            if action == 'supprimer':
                data.pop(index)
            elif action == 'modifier_statut':
                nouveau_statut = request.form.get('statut')
                data[index]['statut'] = nouveau_statut

            save_data(data)
            return redirect(url_for('admin'))

    return render_template('admin.html', factures=data)

# --- Téléchargement ---
@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

# --- Lancement de l'app ---
if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
