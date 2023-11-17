from flask import Flask, render_template, request, redirect, session
import sqlite3 as sql
import uuid #GERA UM NOME ALEATÓRIO PARA A IMAGEM QUE SERÁ SALVA
import os 

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
    produtos = conexao.execute('SELECT * FROM produtos ORDER BY id_prod DESC').fetchall()
    conexao.close()
    titulo = "Página Inicial"
    if verificaSessao() is True:
        login = True
    else:
        login = False
    return render_template("index.html",produtos=produtos,login=login,titulo=titulo)

#ROTA DA PÁGINA DE BUSCA
@app.route("/buscar",methods=["post"])
def buscar():
    busca=request.form["buscar"]
    conexao = conecta_database()
    produtos = conexao.execute('SELECT * FROM produtos WHERE nome_prod LIKE "%" || ? || "%"',(busca,)).fetchall()
    titulo = "Página Inicial"
    return render_template("index.html",produtos=produtos,titulo=titulo)

#ROTA PARA PÁGINA SOBRE
@app.route('/sobre')
def sobre():
    titulo = "Quem Somos"
    return render_template("sobre.html",login=login,titulo=titulo)


#ROTA PARA ÁREA DO ADMINISTRADOR
@app.route('/areaDoAdministrador')
def areaDoAdministrador():    
    if not verificaSessao():
        titulo = "Login"
        return render_template('login.html',login=login,titulo=titulo)
    else:
        iniciar_db()
        conexao = conecta_database()
        produtos = conexao.execute('SELECT * FROM produtos ORDER BY id_prod DESC').fetchall()
        conexao.close()
        titulo = "Administração"
        return render_template('adm.html',login=login,titulo=titulo,produtos=produtos)
    
#ROTA PARA VERIFICAR LOGIN
@app.route('/acesso', methods=['POST'])
def acesso():
    global usuario, senha
    usuario_informado = request.form["usuario"]
    senha_informada = request.form["senha"]
    if (usuario == usuario_informado) and (senha == senha_informada):
        session['login'] = True
        return redirect("/areaDoAdministrador") #ENVIA PARA A ÁREA DO ADMINISTRADOR
    else:
        return render_template("login.html",msg="Usuário ou Senha estão incorretos!") #ABRE LOGIN NOVAMENTE, MAS COM UMA MENSAGEM
    
#ROTA PARA PÁGINA DE CADASTRO
@app.route("/cadprodutos")
def cadprodutos():
    if verificaSessao():
        titulo = "Cadastro de produtos"
        return render_template("cadprodutos.html",titulo=titulo)
    else:
        return redirect("/login")
    
#ROTA DA PÁGINA DE CADASTRO NO BANCO
@app.route("/cadastro",methods=["post"])
def cadastro():
    if verificaSessao():
        nome_prod = request.form['nome_prod']
        desc_prod = request.form['desc_prod']
        preco_prod = request.form['preco_prod'].replace(".",",")
        img_prod = request.files['img_prod']
        id_foto = str(uuid.uuid4().hex)
        filename = id_foto+nome_prod+'.png'
        img_prod.save("static/img/produtos/"+filename)
        conexao = conecta_database()
        conexao.execute('INSERT INTO produtos (nome_prod, desc_prod, preco_prod, img_prod) VALUES (?, ?, ?, ?)',(nome_prod, desc_prod, preco_prod, filename))
        conexao.commit()
        conexao.close()
        return redirect("/areaDoAdministrador")
    else:
        return redirect("/login")
    
#ROTA PARA SELECIONAR POST PARA EDIÇÃO
@app.route('/editar/<id_prod>')
def editar(id_prod):
    if verificaSessao():
        iniciar_db()
        conexao = conecta_database()
        produto = conexao.execute('SELECT * FROM produtos WHERE id_prod = ?',(id_prod,)).fetchall()
        conexao.close()
        return render_template("editar.html",produto=produto)
    else:
        return redirect("/areaDoAdministrador")
    
#ROTA PARA TRATAR A EDIÇÃO DO POST
@app.route('/editpost',methods=['POST'])
def editpost():
    id_prod = request.form['id_prod']
    nome_prod = request.form['nome_prod']
    desc_prod = request.form['desc_prod']
    preco_prod = request.form['preco_prod'].replace(".",",")
    img_prod = request.files['img_prod']
    if not img_prod:
        conexao = conecta_database()
        conexao.execute('UPDATE produtos SET nome_prod = ?, desc_prod = ?, preco_prod = ? WHERE id_prod = ?',(nome_prod,desc_prod,preco_prod,id_prod))
        conexao.commit()
        conexao.close()
    else:
        conexao = conecta_database()
        imagem = conexao.execute('SELECT img_prod FROM produtos WHERE id_prod = ?',(id_prod,)).fetchone()
        imagem = imagem[0]
        img_prod.save("static/img/produtos/"+str(imagem))
        conexao.execute('UPDATE produtos SET nome_prod = ?, desc_prod = ?, preco_prod = ?, img_prod = ? WHERE id_prod = ?',(nome_prod,desc_prod,preco_prod,imagem,id_prod))
        conexao.commit()
        conexao.close()
    return redirect("/areaDoAdministrador")
    
#ROTA PARA EXCLUIR PRODUTOS
@app.route('/excluir/<id>')
def excluir(id):
    if verificaSessao():
        conexao = conecta_database()
        imagem = conexao.execute('SELECT img_prod FROM produtos WHERE id_prod = ?',(id,)).fetchone()
        imagem = imagem[0]
        caminho = os.path.join("static","img","produtos",imagem)
        os.remove(caminho)
        conexao.execute('DELETE FROM produtos WHERE id_prod = ?',(id,))
        conexao.commit()
        conexao.close()
        return redirect("/areaDoAdministrador")
    else:
        return redirect("/areaDoAdministrador")
    
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