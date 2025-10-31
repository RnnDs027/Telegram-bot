import telebot
import os
import mysql.connector

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

except mysql.connector.Error as err:
  print(f"Erro ao conectar ao MySQL: {erro}")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")


TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
   print("ERRO: BOT_TOKEN não encontrado nas variáveis de ambiente! ")

bot = telebot.TeleBot(TOKEN)

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

@bot.message_handler(func=lambda message: True)
def resposta(message):
    chat_id = message.chat.id
    bot.reply_to(message,"Bem vindo as consultas da Fazenda" )
    msg = bot.send_message(chat_id,"Escolha um numero\n" \
    " 1 ---- Consultas \n" \
    " 2 ---- Pedido de compras\n")
    
    
    
    bot.register_next_step_handler(msg,processamento_da_consulta)

def processamento_da_consulta(pda):
    texto = pda.text.lower()
    chat_id = pda.chat.id

    if texto == "1":
        bot.reply_to(pda,"Voce esta entrando nas consultas\n")
        msg_consulta = bot.send_message(chat_id,"O que deseja consultar?\n" \
      " 1 ---- EPI \n" \
      " 2 ---- Fertilizantes\n")
        
        
    elif texto == "2":
       msg_compra = bot.send_message(chat_id,"O que deseja comprar?\n" \
        " 1 ---- EPI \n" \
        " 2 ---- Fertilizantes\n")
    bot.register_next_step_handler(msg_compra, registro_de_compra)

def registro_de_compra(compra_msg):
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
        bot.register_next_step_handler(compra_msg, processar_compra, user_id) 

    if escolha == "2":
        item_pedido = "Fertilizantes"


def processar_compra(compra_msg,user_id):
    global db, cursor
    user_id = str(compra_msg.from_user.id)
    escolha_EPI = compra_msg.text.strip()

    if escolha_EPI == "1":
     escolha_EPI = "Capacete"          

    elif escolha_EPI == "2":
        escolha_EPI = "Luva"

    elif escolha_EPI == "3":
        escolha_EPI = "Butina"
      
    elif escolha_EPI == "4":
        escolha_EPI = "Protetor uricular"

    elif escolha_EPI == "5":
        escolha_EPI = "Oculos"

    sql = """
        INSERT INTO pedidos_compra (user_id, categoria_item)
        VALUES (%s,%s)
        """
    Valores = (user_id, escolha_EPI)
    cursor.execute(sql, Valores)
    db.commit()
    bot.reply_to(compra_msg,f"Pedido de compra para '{escolha_EPI} finalizado com sucesso'")















bot.polling()

