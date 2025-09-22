from flask import render_template, request, redirect, url_for
from models.game import Game
#request é um pacote nativo do flask

players = ['Pedro', 'João', 'Marcos', 'Maria']
game1 = Game('Título 1', 'Ano 1', 'Category 1')
game2 = Game('Título 2', 'Ano 2', 'Category 2')
gameList = [
    game1,
    game2
]

def init_app(app):
    @app.route('/', methods=['GET']) #View Function
    def root():
        title = 'Hello World!'
            
        return render_template('index.html', title=title, players=players)

    @app.route('/games', methods=['GET', 'POST'])
    def games(): #View Function
        games = {'Título' : 'CS-GO', 'Ano' : 2012, 'Categoria' : 'FPS Online'}
        
        #Tratando requisição post com request
        #Só cai aqui se vier uma requisição do tipo post
        if request.method == 'POST':
            #Coletando texto da input:
            if request.form.get('playerInput'):
                players.append(request.form.get('playerInput'))
                return redirect(url_for('newgame'))
            
        return render_template('games.html', games=games, players=players)
    
    @app.route('/newgame', methods=['GET', 'POST'])
    def newgame(): #View Function
        if request.method == 'POST':
            #Coletando texto da input:
            if request.form.get('titleInput') and request.form.get('yearInput') and request.form.get('categoryInput'):
                gameList.append(Game(request.form.get('titleInput'), request.form.get('yearInput'), request.form.get('categoryInput'))) 
                return redirect(url_for('newgame'))
        
        return render_template('newgame.html', gameList=gameList)