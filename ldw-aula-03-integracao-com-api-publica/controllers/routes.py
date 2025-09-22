from flask import render_template, url_for
import json # Conversão dos dados
import urllib #Envia Requisições a uma URL

def init_app(app):
    @app.route("/", methods=['GET'])
    def index():
        return render_template('index.html')
    
    @app.route('/apigames', methods=['GET', 'POST'])
    @app.route('/apigames/<string:id>', methods=['GET', 'POST'])
    def apigames(id=None):
        url = 'https://www.freetogame.com/api/games'
        response = urllib.request.urlopen(url)
        data = response.read()
        gamesList = json.loads(data)
        print('aaa')
        print(id)
        if id:
            gameInfo = []
            # gameInfo.append([item for game in gamesList if game['id'] == id])
            for game in gamesList:
                if game.get('id') == int(id):
                    gameInfo.append(game)
            
            print(len(gameInfo))
            if len(gameInfo) > 0:
                return render_template('gameinfo.html', gameInfo=gameInfo)
            else:
                return f'Game com a ID {id} não encontrado!'
        else:
            return render_template('apigames.html', games=gamesList)