import telebot

TOKEN = "8051534131:AAGfxoboyj6vJv59l3fWHX0oFvqAAPI7jww"

bot = telebot.TeleBot(TOKEN)

    
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

    if texto == "1":
        bot.reply_to(pda,"Voce esta entrando nas consultas\n")
        bot.reply_to(pda,"O que deseja consultar?\n" \
      " 1 ---- EPI \n" \
      " 2 ---- Fertilizantes\n")
        
    elif texto == "2":
     bot.reply_to(pda,"O que deseja comprar?\n" \
        " 1 ---- EPI \n" \
        " 2 ---- Fertilizantes\n")





bot.polling()