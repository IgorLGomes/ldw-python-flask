from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150))
    artist = db.Column(db.String(150))
    ano_lancamento = db.Column(db.Date)
    
    def __init__(self, nome, artist, ano_lancamento):
        self.nome = nome
        self.artist = artist
        self.ano_lancamento = ano_lancamento
        
class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150))
    genero = db.Column(db.String(150))
    
    def __init__(self, nome, genero):
        self.nome = nome
        self.genero = genero
        