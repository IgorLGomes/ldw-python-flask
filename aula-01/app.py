from flask import Flask, render_template #Importando
#flask é o nome do pacote 
#Flask é o nome do que está sendo importado, a classe, etc..

app = Flask(__name__, template_folder='views')
# __name__ representa o nome da aplicação
#Em vez d aaplicação receber app.py vai receber como __main__ em determinado momento

#Definindo a rota principal da aplicação:
#Posteriormente iremos separar para um arquivo rotass
@app.route('/')
def home(): # A função que é executada quando se entra em uma rota é chamada de view function
    #return '<h1>Esta é a primeira aplicação Flask</h1>'
    return render_template('index.html')

@app.route('/games')
def games(): # A função que é executada quando se entra em uma rota é chamada de view function
    title = 'Tarisland'
    year = 2022
    category = 'MMORPG'
    #return '<h1>Esta é a primeira aplicação Flask</h1>'
    players = ["Diego", "Igor", "Tutuisss"]
    #Dicionários Python:
    #Objeto:
    console = {'nome' : 'Playstation 5', 'publisher': 'Sony', 'year' : 2020} #No python tem que converter de dicionário para json e de json para dicionário
    game = {
        'titulo':'tituloDoGame',
        'ano':2005,
    }
    return render_template('games.html', game=title, year=year, category=category, players=players, console=console, gameObject=game)


#app.run() #Iniciando o servidor!
#Só vai rodar o servidor se o arquivo estiver sendo executado a partir do python app.py
#Ou seja se for executado diretamente pelo interpretador vai iniciar o servidor
if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)#DebugMode funciona igual o nodemon
#PARA RODAR VAMOS FAZER python app.py