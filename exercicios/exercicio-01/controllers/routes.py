from flask import render_template, request, redirect, url_for, jsonify

albums_list = [
    {"title": "Magic, Alive!", "filename": "magicalive.jpeg"},
    {"title": "Bottomless Pit", "filename": "bottomlesspit.jpg"},
    {"title": "JOECHILLWORLD", "filename": "joechill.jpeg"},
    {"title": "Alfredo 2", "filename": "alfredo.jpeg"},
    {"title": "Atrocity Exhibition", "filename": "altrocity.jpg"},
    {"title": "Days Before Rodeo", "filename": "dbr.jpeg"},
    {"title": "Let God Sort Em Out", "filename": "lgseo.jpg"},
    {"title": "Ignorance Is Bliss", "filename": "iisb.jpg"},
    {"title": "Calzone Tapes 3", "filename": "calzone3.jpg"},
    {"title": "Yeezus", "filename": "yeezus.jpeg"},
    {"title": "Die Lit", "filename": "dielit.jpg"},
    {"title": "Igor", "filename": "igor.jpg"},
    {"title": "I Lay Down My Life for You", "filename": "ildmly.jpeg"},
    {"title": "The Life of Pablo", "filename": "tlop.jpeg"},
    {"title": "If Looks Could Kill", "filename": "ilck.jpeg"},
    {"title": "Time 'n' Place", "filename": "tnp.jpg"},
    {"title": "Cartola (1976)", "filename": "cartola.jpg"},
]

# dicionário que será exibido em tabela e pode ser atualizado
artist_dict = {
    "name": "Kanye West",
    "album": "Yeezus",
    "year": 2013,
    "genre": "Hip-Hop"
}


def init_app(app):
    @app.route('/', methods=['GET'])
    def index():
        # pagina inicial com navbar; passa dados resumo opcional
        qtd_albuns = len(albums_list)
        return render_template('index.html', albums_list=albums_list, qtd_albuns=qtd_albuns)

    @app.route('/albums', methods=['GET', 'POST'])
    def albums():
        # rota que mostra a lista e permite inclusão via form
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            filename = request.form.get('filename', '').strip()

            if title and filename:
                albums_list.append({"title": title, "filename": filename})
            return redirect(url_for('albums'))

        return render_template('albums.html', albums=albums_list)

    @app.route('/artist', methods=['GET', 'POST'])
    def artist():
        # rota que mostra o dicionário em tabela e permite atualização
        global artist_dict
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            album = request.form.get('album', '').strip()
            year = request.form.get('year', '').strip()
            genre = request.form.get('genre', '').strip()

            if name and album and year and genre:
                # tentativa de converter ano para int, se falhar mantem string
                try:
                    year_val = int(year)
                except ValueError:
                    year_val = year
                artist_dict = {
                    "name": name,
                    "album": album,
                    "year": year_val,
                    "genre": genre
                }
            return redirect(url_for('artist'))

        return render_template('artist.html', artist=artist_dict)

    # endpoints JSON opcionais para consumo por API
    @app.route('/api/albums', methods=['GET'])
    def api_albums():
        return jsonify(albums_list)

    @app.route('/api/artist', methods=['GET'])
    def api_artist():
        return jsonify(artist_dict)
