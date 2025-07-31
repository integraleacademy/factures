@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    data = load_data()

    if request.method == 'POST':
        action = request.form.get('action')
        index_str = request.form.get('index')

        if index_str is not None and index_str.isdigit():
            index = int(index_str)

            if action == 'delete':
                fichier = data[index]['fichier']
                try:
                    os.remove(os.path.join(UPLOAD_FOLDER, fichier))
                except:
                    pass
                data.pop(index)
            elif action == 'update':
                data[index]['statut'] = request.form.get('statut')
                data[index]['commentaire'] = request.form.get('commentaire')
            save_data(data)
        else:
            print("⚠️ Requête POST reçue sans index valide.")

    return render_template('admin.html', factures=data)
