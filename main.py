from flask import Flask, render_template, request, redirect, session
import sqlite3 as sql

app = Flask(__name__)
app.secret_key = "produtosdoseuze"

usuario = 'SeuZé'
senha = '#53uZ33Mu1T0L3G4L'
login = False

#Se houver uma conta logada, ela será deslogada
def verificaSessao():
    if "login" in session and session["login"]:
        return True
    else:
        return False
    
#CONEXÃO COM BANCO DE DADOS
def conecta_database():
    conexao = sql.connect("db_quitanda.db")
    conexao.row_factory = sql.Row
    return conexao

#INICIAR O BANCO DE DADOS
def iniciar_db():
    conexao = conecta_database()
    with app.open_resource('database.sql', mode='r') as comandos:
        conexao.cursor().executescript(comandos.read())
    conexao.commit() # Cria a tabela se não existir
    conexao.close()

#ROTA INICIAL
@app.route('/')
def index():
    global login
    iniciar_db() #CHAMANDO O DB
    conexao = conecta_database()
    produtos = conexao.execute('SELECT * FROM produtos ORDER BY id DESC').fetchall()
    conexao.close()
    if verificaSessao() is True:
        login = True
    else:
        login = False
    return render_template("index.html",produtos=produtos,login=login)

#ROTA PARA PÁGINA SOBRE
@app.route('/sobre')
def sobre():
    return render_template("sobre.html",login=login)


#ROTA PARA FAZER O LOGIN
@app.route('/loginDoAdministrador')
def fazerLogin():
    if login is False:
        return render_template('login.html')
    else:
        return redirect("/",msg="Administrador já está logado!") #RETORNA PARA A HOMEPAGE, MAS COM UMA MENSAGEM
    
#ROTA PARA VERIFICAR LOGIN
@app.route('/acesso', methods=['POST'])
def acesso():
    global usuario, senha
    usuario_informado = request.form["usuario"]
    senha_informada = request.form["senha"]
    if (usuario == usuario_informado) and (senha == senha_informada):
        session['login'] = True
        return redirect("/") #VOLTA PARA HOMEPAGE
    else:
        return render_template("login.html",msg="Usuário ou Senha estão incorretos!") #ABRE LOGIN NOVAMENTE, MAS COM UMA MENSAGEM
    
#ROTA PARA LOGOFF
@app.route('/logoff')
def logoff():
    global login
    login = False
    session.clear()
    return redirect('/')

#FINAL DO CÓDIGO - EXECUTANDO O SERVIDOR
if __name__ == '__main__':
    app.run(debug=True)