import os
import json
import time
from flask import Flask, render_template, request, redirect, send_from_directory

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
DATA_FILE = '/data/data.json'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        fichier = request.files['facture']
        if fichier.filename == '':
            return redirect('/')
        timestamp = time.strftime("%Y%m%d%H%M%S")
        nom_fichier = f"{timestamp}_{fichier.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, nom_fichier)
        fichier.save(filepath)

        data = load_data()
        data.append({
            'nom': nom_fichier,
            'chemin': filepath,
            'statut': 'Non traité',
            'commentaire': ''
        })
        save_data(data)

        return render_template('index.html', message="Facture déposée avec succès.")
    return render_template('index.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    data = load_data()
    if request.method == 'POST':
        try:
            index = int(request.form.get('index'))
            if 0 <= index < len(data):
                data[index]['statut'] = request.form.get('statut')
                data[index]['commentaire'] = request.form.get('commentaire')
                save_data(data)
        except Exception as e:
            print("Erreur admin:", e)
    return render_template('admin.html', factures=data)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route('/delete/<int:index>', methods=['POST'])
def delete(index):
    data = load_data()
    if 0 <= index < len(data):
        try:
            os.remove(data[index]['chemin'])
        except FileNotFoundError:
            pass
        del data[index]
        save_data(data)
    return redirect('/admin')

if __name__ == '__main__':
    app.run(debug=True)
