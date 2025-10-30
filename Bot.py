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
   sql = """
          INSERT INTO user_notes (user_id,note_text)
          VALUES(%s, %s)
          ON DUPLICATE KEY UPDATE note_text = %s

          """
     valores = (user_id , text_to_save, text_to_save)
     cursor.execute(sql,valores)
     db.commit()

bot.reply_to(message,f"Salvo '{text_to_save}'")

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
    user_id = compra_msg.from_user.id
    escolha = compra_msg.text.strip()
    item_pedido = ""

    if escolha == "1":
        item_pedido = "EPI"

    elif escolha == "2":
        item_pedido = "Fertilizantes"
    
    texto_para_salvar = f"Pedido de compra: {item_pedido}"

    sql = """
        INSERT INTO user_notes (user_id, note_text)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE note_text = %s
    """
    valores = (user_id, texto_para_salvar, texto_para_salvar)

    cursor.execute(sql, valores)
    db.commit()
    bot.reply_to(compra_msg, f"✅ Pedido de compra para '{item_pedido}' registrado!")


bot.polling()