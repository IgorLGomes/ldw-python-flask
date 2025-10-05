import os
import base64
import secrets
import requests
from urllib.parse import urlencode
from models.database import db, Album, Artist
from flask import render_template, request, redirect, url_for, jsonify, session, abort


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

# Spotify config via env
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
# ex: http://127.0.0.1:4000/spotify/callback
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE = "https://api.spotify.com/v1"


def _basic_auth_header(client_id, client_secret):
    token = f"{client_id}:{client_secret}".encode()
    return {"Authorization": "Basic " + base64.b64encode(token).decode()}


def _refresh_access_token(refresh_token):
    headers = _basic_auth_header(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    resp = requests.post(SPOTIFY_TOKEN_URL, data=data, headers=headers)
    resp.raise_for_status()
    return resp.json()  # contém access_token possivelmente novo


def _spotify_get(endpoint, access_token, params=None):
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(f"{SPOTIFY_API_BASE}{endpoint}",
                        headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()


def init_app(app):
    @app.route('/', methods=['GET'])
    def index():
        qtd_albuns = len(albums_list)
        return render_template('index.html', albums_list=albums_list, qtd_albuns=qtd_albuns)

    @app.route('/albums', methods=['GET', 'POST'])
    def albums():
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            filename = request.form.get('filename', '').strip()
            if title and filename:
                albums_list.append({"title": title, "filename": filename})
            return redirect(url_for('albums'))
        return render_template('albums.html', albums=albums_list)

    # ---------------- Spotify OAuth ----------------
    @app.route('/spotify')
    def spotify_home():
        # página que mostra botão de login ou dados se já autorizado
        logged = 'spotify_access_token' in session
        return render_template('spotify.html', logged=logged)


    @app.route("/spotify/login")
    def spotify_login():
        auth_url = "https://accounts.spotify.com/authorize"
        state = secrets.token_urlsafe(16)   # gera string segura
        session["oauth_state"] = state      # salva na sessão

        params = {
            "client_id": os.getenv("SPOTIFY_CLIENT_ID"),
            "response_type": "code",
            "redirect_uri": os.getenv("SPOTIFY_REDIRECT_URI"),
            "scope": "user-top-read",
            "state": state,
        }
        return redirect(f"{auth_url}?{urlencode(params)}")


    @app.route("/spotify/callback")
    def spotify_callback():
        code = request.args.get("code")
        state = request.args.get("state")

        # confere state
        if state != session.get("oauth_state"):
            abort(400, description="Invalid state parameter")

        # troca code por tokens
        headers = _basic_auth_header(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": SPOTIFY_REDIRECT_URI,
        }
        resp = requests.post(SPOTIFY_TOKEN_URL, data=data, headers=headers)
        if resp.status_code != 200:
            return f"Token exchange failed: {resp.text}", 400

        token_data = resp.json()
        session['spotify_access_token'] = token_data.get('access_token')
        session['spotify_refresh_token'] = token_data.get('refresh_token')
        session['spotify_token_expires_in'] = token_data.get('expires_in')

        return redirect(url_for('spotify_top'))


    @app.route('/spotify/top')
    def spotify_top():
        # exibe top artists e top tracks (catálogo + item individual)
        access_token = session.get('spotify_access_token')
        refresh_token = session.get('spotify_refresh_token')
        if not access_token:
            return redirect(url_for('spotify_home'))
        try:
            top_artists = _spotify_get(
                "/me/top/artists", access_token, params={"limit": 15,  "time_range": "long_term"}
                )
            top_tracks = _spotify_get(
                "/me/top/tracks", 
                access_token, 
                params={"limit": 50, "time_range": "long_term"}  
            )

        except requests.HTTPError as e:
            # se token expirou, tenta refresh
            resp = e.response
            if resp is not None and resp.status_code == 401 and refresh_token:
                new_tokens = _refresh_access_token(refresh_token)
                new_access = new_tokens.get("access_token")
                if new_access:
                    session['spotify_access_token'] = new_access
                    access_token = new_access
                    top_artists = _spotify_get(
                        "/me/top/artists", access_token, params={"limit": 10})
                    top_tracks = _spotify_get(
                        "/me/top/tracks", access_token, params={"limit": 10})
                else:
                    return redirect(url_for('spotify_home'))
            else:
                return f"Erro ao chamar API do Spotify: {resp.text if resp is not None else str(e)}", 500

        # estrutura simples para template
        artists = top_artists.get('items', [])
        tracks = top_tracks.get('items', [])
        return render_template('spotify_top.html', artists=artists, tracks=tracks)

    @app.route('/spotify/logout')
    def spotify_logout():
        session.pop('spotify_access_token', None)
        session.pop('spotify_refresh_token', None)
        return redirect(url_for('spotify_home'))




    @app.route('/artist', methods=['GET', 'POST'])
    @app.route('/artist/delete/<int:id>')
    def artist(id=None):
        if id:
            artist = Artist.query.get(id)
            # Deleta o console cadastro pela ID
            db.session.delete(artist)
            db.session.commit()
            return redirect(url_for('artist'))
        if request.method == 'POST':
            newartist = Artist(
                request.form['nome'], request.form['genero'])
            db.session.add(newartist)
            db.session.commit()
            return redirect(url_for('artist'))
        else:
            # Captura o valor de 'page' que foi passado pelo método GET
            # Define como padrão o valor 1 e o tipo inteiro
            page = request.args.get('page', 1, type=int)
            # Valor padrão de registros por página (definimos 3)
            per_page = 3
            # Faz um SELECT no banco a partir da pagina informada (page)
            # Filtrando os registro de 3 em 3 (per_page)
            artist = Artist.query.paginate(
                page=page, per_page=per_page)
            return render_template('artist.html', artist=artist)

    # CRUD artist - EDIÇÃO
    @app.route('/artist/edit/<int:id>', methods=['GET', 'POST'])
    def artistEdit(id):
        artist = Artist.query.get(id)
        # Edita o console com as informações do formulário
        if request.method == 'POST':
            artist.nome = request.form['nome']
            artist.genero = request.form['genero']
            db.session.commit()
            return redirect(url_for('artist'))
        return render_template('artistedit.html', artist=artist)
    
    
    
    
    
    
    # CRUD albums - LISTAGEM, CADASTRO E EXCLUSÃO
    @app.route('/albums/colecao', methods=['GET', 'POST'])
    @app.route('/albums/colecao/delete/<int:id>')
    def albumsColecao(id=None):
        if id:
            album = Album.query.get(id)
            # Deleta o console cadastro pela ID
            db.session.delete(album)
            db.session.commit()
            return redirect(url_for('albumsColecao'))
        # Cadastra um novo console
        if request.method == 'POST':
            newalbum = Album(
                request.form['nome'], request.form['artist'], request.form['ano_lancamento'])
            db.session.add(newalbum)
            db.session.commit()
            return redirect(url_for('albumsColecao'))
        else:
            # Captura o valor de 'page' que foi passado pelo método GET
            # Define como padrão o valor 1 e o tipo inteiro
            page = request.args.get('page', 1, type=int)
            # Valor padrão de registros por página (definimos 3)
            per_page = 3
            # Faz um SELECT no banco a partir da pagina informada (page)
            # Filtrando os registro de 3 em 3 (per_page)
            albums_page = Album.query.paginate(
                page=page, per_page=per_page)
            artists = Artist.query.all()
            return render_template('albumscolecao.html', albumscolecao=albums_page, artists=artists)
        
    # CRUD albums - EDIÇÃO
    @app.route('/albums/edit/<int:id>', methods=['GET', 'POST'])
    def albumEdit(id):
        album = Album.query.get(id)
        # Edita o console com as informações do formulário
        if request.method == 'POST':
            album.nome = request.form['nome']
            album.artist = request.form['artist']
            album.ano_lancamento = request.form['ano_lancamento']
            db.session.commit()
            return redirect(url_for('albumsColecao'))
        artists = Artist.query.all()
        return render_template('albumedit.html', album=album, artists=artists)