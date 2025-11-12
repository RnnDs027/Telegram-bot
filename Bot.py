#IMPORTAÇÃO DAS BIBLIOTECAS
import telebot
import os
import mysql.connector

#CONEXAO COM BANCO DE DADOS
db_host = os.environ.get('MYSQLHOST')
db_user = os.environ.get('MYSQLUSER')
db_password = os.environ.get('MYSQLPASSWORD')
db_name = os.environ.get('MYSQLDATABASE')
db_port = os.environ.get('MYSQLPORT')

try:
   db = mysql.connector.connect(
      host=db_host,
      user=db_user,
      password=db_password,
      database=db_name,
      port=int(db_port),
   )
   cursor = db.cursor()
   print("--- CONEXÃO COM O BANCO DE DADOS FOI UM SUCESSO! O cursor foi criado. ---")

except mysql.connector.Error as err:
    print(f"Erro ao conectar ao MySQL: {err}") 
    print("--- FALHA NA CONEXÃO! O cursor NÃO foi criado! ---") # <--- ADICIONE ISSO
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")
    print("--- FALHA NA CONEXÃO! O cursor NÃO foi criado! ---")

#CONEXÃO COM O BOT DO TELEGRAM
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
   print("ERRO: BOT_TOKEN não encontrado nas variáveis de ambiente! ")
bot = telebot.TeleBot(TOKEN)

#INCIO DO CODIGO
@bot.message_handler(commands=['salvar'])
def save_note(message):
    user_id = message.from_user.id
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1:
        text_to_save = parts[1].strip()
        sql = """
        INSERT INTO user_notes (user_id,note_text)
        VALUES(%s, %s)
        ON DUPLICATE KEY UPDATE note_text = %s
        """
    valores = (user_id , text_to_save, text_to_save)
    try:
     cursor.execute(sql,valores)
     db.commit()
     bot.reply_to(message,f"Salvo '{text_to_save}'")
    except Exception as e:
     bot.reply_to(message, f"Erro ao salvar no banco: {e}")
    else:
        bot.reply_to(message, "Use /salvar <texto para salvar>")

#INICIO DA CHAMADA DO BOT
@bot.message_handler(func=lambda message: True)
def primeira_pergunta_bot(message):
    chat_id = message.chat.id
    bot.reply_to(message,"Bem vindo as consultas da Fazenda" )
    msg = bot.send_message(chat_id,"Escolha um numero\n" \
    " 1 ---- Consultas \n\n\n" \
    " 2 ---- Pedido de compras\n")
    bot.register_next_step_handler(msg,escolha_de_avanço)

def escolha_de_avanço(pda):
    texto = pda.text.lower()
    chat_id = pda.chat.id

    if texto == "1":
        bot.reply_to(pda,"Voce esta entrando nas consultas\n")
        msg_consulta = bot.send_message(chat_id,"O que deseja consultar?\n" \
      " 1 ---- EPI \n" \
      " 2 ---- Fertilizantes\n")
        
        bot.register_next_step_handler(msg_consulta, escolha_de_qual_consulta)
        
    elif texto == "2":
        msg_compra = bot.send_message(chat_id,"O que deseja adicionar ao estoque??\n" \
        " 1 ---- EPI \n\n\n" \
        " 2 ---- Fertilizantes\n")
        bot.register_next_step_handler(msg_compra, escolha_soma_do_estoque)

def escolha_de_qual_consulta(msg):
    escolha = msg
    if escolha == "1":
        consulta_epi
    elif escolha =="2":
        consulta_fertilizante

def escolha_soma_do_estoque(msg):
    escolha = msg
    if escolha == "1":
        registro_de_soma_epi
    elif escolha =="2":
        registro_de_soma_fertilizante

#TODAS AS FUNÇOES DE FERTILIZANTE
def consulta_fertilizante(msg):
    global db,cursor
    cursor.execute("SELECT * FROM soma_fertilizante")
    registros = cursor.fetchall()
    resposta = ("*Itens cadastrados no banco de dados* \n\n")
    for linha in registros:
        codigo_item = linha[0]
        categoria_item = linha[2]
        quantidade = linha[3]
        resposta = resposta + (f"Id produto - {codigo_item}\n Item - {categoria_item}\n Quantidade - {quantidade}\n\n")
    bot.reply_to(msg,resposta)


#TODAS AS FUNÇÕES PARA EPI
def consulta_epi(msg):
    global db, cursor
    cursor.execute("SELECT * FROM pedidos_compras")
    registros = cursor.fetchall()
    resposta = ("*Itens cadastrados no banco de dados*\n\n")
    for linha in registros:
        codigo_item = linha[0]
        categoria_item = linha[2]
        quantidade = linha[3]
        resposta = resposta + (f"Id produto - {codigo_item}\n Item - {categoria_item}\n Quantidade - {quantidade}\n\n")
    bot.reply_to(msg,resposta)

def registro_de_soma_epi(compra_msg):
    global db, cursor
    user_id = str(compra_msg.from_user.id)
    escolha = compra_msg.text.strip()
    escolha_EPI = ""

    if escolha == "1":
        escolha_EPI = compra_msg.text.strip()
        bot.reply_to(compra_msg,"Escolha um numero \n" \
        "1 ---- Capacete\n" \
        "2 ---- Luva \n" \
        "3 ---- Butina\n" \
        "4 ---- Protetor uricular\n" \
        "5 ---- Oculos\n")
        bot.register_next_step_handler(compra_msg, quantidade_epi, user_id) 

    if escolha == "2":
        item_pedido = "Fertilizantes"
    
def quantidade_epi(compra_msg,user_id):
   global db, cursor
   Escolha_epi = compra_msg.text.strip() 
   bot.reply_to(compra_msg,"Qual a quantidade voce deseja adicionar ao estoque?")
   bot.register_next_step_handler(compra_msg,processar_compra_epi,Escolha_epi,user_id)

def processar_compra_epi(quantidade_msg,Escolha_epi,user_id):
    global db, cursor
    quantidade = int(quantidade_msg.text.strip())

    if Escolha_epi == "1":
     Escolha_epi = "Capacete"          

    elif Escolha_epi == "2":
        Escolha_epi = "Luva"

    elif Escolha_epi == "3":
        Escolha_epi = "Butina"
      
    elif Escolha_epi == "4":
        Escolha_epi = "Protetor uricular"

    elif Escolha_epi == "5":
        Escolha_epi = "Oculos"

    cursor.execute(
         "SELECT quantidade FROM pedidos_compras WHERE categoria_item = %s AND user_id = %s",
         (Escolha_epi,user_id)
     )
    resultado = cursor.fetchone()
    quantidade_atual = resultado[0]
    nova_quantidade = quantidade + quantidade_atual

    cursor.execute(
        "UPDATE pedidos_compras SET quantidade = %s WHERE  categoria_item = %s AND user_id = %s",
        (nova_quantidade,Escolha_epi,user_id)
    )
    db.commit()
    bot.reply_to(quantidade_msg,f"Seu pedido de compra do item {Escolha_epi} realizado com sucesso")


   













bot.polling()
