#IMPORTAÇÃO DAS BIBLIOTECAS
import telebot
from telebot import types
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

Autorizados = {5007489215}

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
    #Adição de botões
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    btn1 = types.KeyboardButton("Consultas")
    btn2 = types.KeyboardButton("Adicionar ao estoque")
    btn3 = types.KeyboardButton("Remover do estoque")
    markup.add(btn1,btn2,btn3)

    #Inicio da interface do usuario
    bot.reply_to(message,"Bem-vindo às consultas da Fazenda" )
    msg = bot.send_message(chat_id,"Escolha um número\n" \
    " Consultas \n\n" \
    " Adicionar ao estoque \n\n" \
    " Remover do estoque",reply_markup=markup)
    #Mandando a mensagem salva para a proxima função
    bot.register_next_step_handler(msg,escolha_de_avanço)

def escolha_de_avanço(pda):
    texto = pda.text
    chat_id = pda.chat.id
    user_id = pda.from_user.id

    if texto == "Consultas":
        #Adição dos botões
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        btn1 = types.KeyboardButton("EPI")
        btn2 = types.KeyboardButton("Fertilizantes")
        btn3 = types.KeyboardButton("Voltar")
        markup.add(btn1,btn2,btn3)

        #Interface do usuario
        bot.reply_to(pda,"Voce esta entrando nas consultas\n")
        msg_consulta = bot.send_message(chat_id,"O que deseja consultar?\n" \
      " EPI \n\n" \
      " Fertilizantes\n\n" \
      " Voltar",reply_markup=markup)
        
        #Mandando a mensagem salva para a proxima função
        bot.register_next_step_handler(msg_consulta, escolha_de_qual_consulta)
        
    elif texto == "Adicionar ao estoque":

        if user_id not in Autorizados:
            bot.reply_to(pda, "⚠️ Você não tem permissão para adicionar itens ao estoque.")
            primeira_pergunta_bot
        else:
            #Adição dos botões
            markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
            btn1 = types.KeyboardButton("EPI")
            btn2 = types.KeyboardButton("Fertilizantes")
            btn3 = types.KeyboardButton("Voltar")
            markup.add(btn1,btn2,btn3)

            #Interface do usuario
            bot.reply_to(pda,"Voce esta entrando na adição do estoque\n")
            msg_compra = bot.send_message(chat_id,"O que deseja adicionar ao estoque??\n" \
            " EPI \n\n" \
            " Fertilizantes\n\n" \
            " Voltar",reply_markup=markup)

            #Mandando a mensagem salva para a proxima função
            bot.register_next_step_handler(msg_compra, escolha_adiçao_do_estoque)

    elif texto == "Remover do estoque":

        if user_id not in Autorizados:
            bot.reply_to(pda, "⚠️ Você não tem permissão para adicionar itens ao estoque.")
            escolha_de_avanço(pda)
        else:
            #Adição dos botões
            markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
            btn1 = types.KeyboardButton("EPI")
            btn2 = types.KeyboardButton("Fertilizantes")
            btn3 = types.KeyboardButton("Voltar")
            markup.add(btn1,btn2,btn3)

            #Interface do usuario
            bot.reply_to(pda,"Voce esta entrando na remoção de produtos do estoque")
            msg_compra = bot.send_message(chat_id,"O que deseja remover do estoque?\n\n"
            " EPI \n\n" \
            " Fertilizantes\n\n" \
            " Voltar",reply_markup=markup)

            #Mandando a mensagem salva para a proxima função
            bot.register_next_step_handler(msg_compra,escolha_remover_estoque)

def escolha_de_qual_consulta(msg):
    escolha = msg.text
    if escolha == "EPI":
        bot.reply_to(msg,"voce esta entrando na consulta EPI")
        consulta_epi(msg)
    elif escolha =="Fertilizantes":
        bot.reply_to(msg,"voce esta entrando na consulta Fertilizantes")
        consulta_fertilizante(msg)
    elif escolha =="Voltar":
        bot.reply_to(msg,"voce esta Voltando ao menu principal")
        primeira_pergunta_bot(msg)

def escolha_adiçao_do_estoque(msg):
    escolha = msg.text
    if escolha == "EPI":
        escolha1 = "adição"
        bot.reply_to(msg,"voce esta entrando na adição de estoque EPI")
        registro_epi(msg,escolha1)
    elif escolha =="Fertilizantes":
        escolha1 = "adição"
        bot.reply_to(msg,"voce esta entrando na adição de estoque Fertilizante")
        registro_fertilizante(msg,escolha1)
    elif escolha =="Voltar":
        bot.reply_to(msg,"voce esta Voltando ao menu principal")
        primeira_pergunta_bot(msg)

def escolha_remover_estoque(msg):
    escolha = msg.text
    if escolha == "EPI":
        escolha1 = "remoção"
        registro_epi(msg,escolha1)

    elif escolha == "Fertilizantes":
        escolha1 = "remoção"
        registro_fertilizante(msg,escolha1)

    elif escolha =="Voltar":
        bot.reply_to(msg,"voce esta Voltando ao menu principal")
        primeira_pergunta_bot(msg)

def somar_novamente(msg,novamente):
    #Soma novamente Fertilizante
    if novamente == 1:
        #Adição dos botões
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        btn1 = types.KeyboardButton("Sim")
        btn2 = types.KeyboardButton("Não")
        markup.add(btn1,btn2)
        somar_novamente = msg.text
        if somar_novamente == "Sim":
            bot.reply_to(msg,"Deseja adicionar algo mais no estoque?",reply_markup=markup)
            escolha1 = "adição"
            registro_fertilizante(msg,escolha1)
        elif somar_novamente == "Não" : 
            primeira_pergunta_bot(msg)
    #Remove novamente Fertilizante
    elif novamente == 2:
        bot.reply_to(msg,"Deseja remover algo mais no estoque?")
        #Adição dos botões
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        btn1 = types.KeyboardButton("Sim")
        btn2 = types.KeyboardButton("Não")
        markup.add(btn1,btn2)
        remover_novamente = msg.text
        if remover_novamente == "Sim":
            bot.reply_to(msg,"Deseja remover algo mais no estoque?",reply_markup=markup)
            escolha1 = "remoção"
            registro_fertilizante(msg,escolha1)
        elif remover_novamente == "Sim": 
            primeira_pergunta_bot(msg)
    #Soma novamente EPI
    elif novamente == 3:
        bot.reply_to(msg,"Deseja adicionar algo mais no estoque?")
        #Adição dos botões
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        btn1 = types.KeyboardButton("Sim")
        btn2 = types.KeyboardButton("Não")
        markup.add(btn1,btn2)
        somar_novamente = msg.text
        if somar_novamente == "Sim":
            bot.reply_to(msg,"Deseja adicionar algo mais no estoque?",reply_markup=markup)
            escolha1 = "adição"
            registro_epi(msg,escolha1)
        elif somar_novamente == "Não" : 
            primeira_pergunta_bot(msg)
    #Remove novamente EPI
    elif novamente == 4:
        bot.reply_to("Deseja remover algo mais no estoque?")
        #Adição dos botões
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        btn1 = types.KeyboardButton("Sim")
        btn2 = types.KeyboardButton("Não")
        markup.add(btn1,btn2)
        somar_novamente = msg.text
        if remover_novamente == "Sim":
            bot.reply_to(msg,"Deseja remover algo mais no estoque?",reply_markup=markup)
            escolha1 = "remoção"
            registro_epi(msg,escolha1)
        elif remover_novamente == "Sim": 
            primeira_pergunta_bot(msg)

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

def registro_fertilizante(msg,escolha1):
    global db, cursor
    user_id = str(msg.from_user.id)
    #Adição de botões
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    btn1 = types.KeyboardButton("Adubo")
    btn2 = types.KeyboardButton("Voltar")
    markup.add(btn1,btn2)

    bot.reply_to(msg,"Escolha uma Opção \n" \
    " Adubo\n\n" \
    " Voltar\n\n",reply_markup=markup)
    bot.register_next_step_handler(msg, quantidade_fertilizante, escolha1,user_id)      

def quantidade_fertilizante(msg,escolha1,user_id):
    global db, cursor
    voltar = msg.text
    Escolha_fertilizante = msg.text.strip() 
    if escolha1 == "adição":
        msg_enviada = bot.reply_to(msg,"Qual a quantidade voce deseja adicionar ao estoque?")
        bot.register_next_step_handler(msg_enviada,somar_produto_fertilizante,Escolha_fertilizante,user_id)
    elif escolha1 == "remoção":
        msg_enviada = bot.reply_to(msg,"Qual a quantidade voce deseja remover do estoque?")
        bot.register_next_step_handler(msg_enviada,remover_produto_fertilizante,Escolha_fertilizante,user_id)
    elif voltar =="Voltar":
        bot.reply_to(msg,"voce esta Voltando ao menu principal")
        primeira_pergunta_bot(msg)

def somar_produto_fertilizante(quantidade_msg,Escolha_fertilizante,user_id):
    global db, cursor
    print("Chegou ate aqui normal")
    quantidade = int(quantidade_msg.text.strip())
    

    if Escolha_fertilizante == "Adubo":
     Escolha_fertilizante = "Adubo"    
     print("começou a procurar o produto")      
    cursor.execute(
         "SELECT quantidade_em_sacos FROM soma_fertilizante WHERE categoria_item = %s AND user_id = %s",
         (Escolha_fertilizante,user_id)
     )
    resultado = cursor.fetchone()
    quantidade_atual = resultado[0]
    nova_quantidade = quantidade + quantidade_atual
    print("começou a atualizar")
    cursor.execute(
        "UPDATE soma_fertilizante SET quantidade_em_sacos = %s WHERE  categoria_item = %s AND user_id = %s",
        (nova_quantidade,Escolha_fertilizante,user_id)
    )
    db.commit()
    bot.reply_to(quantidade_msg,f"Seu pedido de adição do item {Escolha_fertilizante} foi realizado com sucesso")
    novamente = 1
    somar_novamente(quantidade_msg,novamente)

def remover_produto_fertilizante(quantidade_msg,Escolha_fertilizante,user_id):
    global db, cursor
    quantidade = int(quantidade_msg.text.strip())

    if Escolha_fertilizante == "Adubo":
     Escolha_fertilizante = "Adubo"         
    cursor.execute(
         "SELECT quantidade_em_sacos FROM soma_fertilizante WHERE categoria_item = %s AND user_id = %s",
         (Escolha_fertilizante,user_id)
     )
    resultado = cursor.fetchone()
    quantidade_atual = resultado[0]
    nova_quantidade = quantidade_atual - quantidade
    if nova_quantidade < 0:
        bot.reply_to(quantidade_msg,"O Estoque não pode ficar negativo. Tente outro valor")
        escolha1 = "remoção"
        bot.register_next_step_handler(quantidade_msg,remover_produto_fertilizante,Escolha_fertilizante,user_id)
    else:
        print("começou a atualizar")    
        cursor.execute(
            "UPDATE soma_fertilizante SET quantidade_em_sacos = %s WHERE  categoria_item = %s AND user_id = %s",
            (nova_quantidade,Escolha_fertilizante,user_id)
        )
        db.commit()
        bot.reply_to(quantidade_msg,f"Seu pedido de remoção do item {Escolha_fertilizante} foi realizado com sucesso")
        novamente = 2
        somar_novamente(quantidade_msg,novamente)

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

def registro_epi(compra_msg,escolha1):
    global db, cursor
    user_id = str(compra_msg.from_user.id)
    #Adição dos botões
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    btn1 = types.KeyboardButton("Capacete")
    btn2 = types.KeyboardButton("Luva")
    btn3 = types.KeyboardButton("Butina")
    btn4 = types.KeyboardButton("Protetor uricular")
    btn5 = types.KeyboardButton("Oculos")
    btn6 = types.KeyboardButton("Voltar")
    markup.add(btn1,btn2,btn3,btn4,btn5,btn6)

    #Interface de usuario
    bot.reply_to(compra_msg,"Escolha um numero \n" \
    " Capacete\n" \
    " Luva \n" \
    " Butina\n" \
    " Protetor uricular\n" \
    " Oculos\n" \
    "\nVoltar",reply_markup=markup)

    #Mandando a mensagem salva para a proxima função
    bot.register_next_step_handler(compra_msg, quantidade_epi,escolha1, user_id) 
    
def quantidade_epi(compra_msg,escolha1,user_id):
    global db, cursor
    Escolha_epi = compra_msg.text

    if escolha1 == "adição":
        Escolha_epi = compra_msg.text 
        msg_enviada = bot.reply_to(compra_msg,"Qual a quantidade voce deseja adicionar ao estoque?")
        bot.register_next_step_handler(msg_enviada,somar_produto_epi,Escolha_epi,user_id)
    elif escolha1 == "remoção":
        Escolha_epi = compra_msg.text 
        msg_enviada = bot.reply_to(compra_msg,"Qual a quantidade voce deseja remover do estoque?")
        bot.register_next_step_handler(msg_enviada,remover_produto_epi,Escolha_epi,user_id)
    elif Escolha_epi =="Voltar":
        bot.reply_to(compra_msg,"voce esta voltando ao menu principal")
        primeira_pergunta_bot(compra_msg)

def somar_produto_epi(quantidade_msg,Escolha_epi,user_id):
    global db, cursor
    quantidade = int(quantidade_msg.text.strip())

    if Escolha_epi == "Capacete":
     Escolha_epi = "Capacete"          

    elif Escolha_epi == "Luva":
        Escolha_epi = "Luva"

    elif Escolha_epi == "Butina":
        Escolha_epi = "Butina"
      
    elif Escolha_epi == "Protetor uricular":
        Escolha_epi = "Protetor uricular"

    elif Escolha_epi == "Oculos":
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
    bot.reply_to(quantidade_msg,f"Seu pedido de adição do item {Escolha_epi} foi realizado com sucesso")
    novamente = 3
    somar_novamente(quantidade_msg,novamente)
    
def remover_produto_epi(quantidade_msg,Escolha_epi,user_id):
    global db, cursor
    quantidade = int(quantidade_msg.text.strip())

    if Escolha_epi == "Capacete":
     Escolha_epi = "Capacete"          

    elif Escolha_epi == "Luva":
        Escolha_epi = "Luva"

    elif Escolha_epi == "Butina":
        Escolha_epi = "Butina"
      
    elif Escolha_epi == "Protetor uricular":
        Escolha_epi = "Protetor uricular"

    elif Escolha_epi == "Oculos":
        Escolha_epi = "Oculos"

    cursor.execute(
         "SELECT quantidade FROM pedidos_compras WHERE categoria_item = %s AND user_id = %s",
         (Escolha_epi,user_id)
     )
    resultado = cursor.fetchone()
    quantidade_atual = resultado[0]
    nova_quantidade = quantidade_atual - quantidade
    if nova_quantidade < 0:
        bot.reply_to(quantidade_msg,"O Estoque não pode ficar negativo. Tente outro valor")
        escolha1 = "remoção"
        bot.register_next_step_handler(quantidade_msg,remover_produto_epi,Escolha_epi,user_id)
    else:
        cursor.execute(
            "UPDATE pedidos_compras SET quantidade = %s WHERE  categoria_item = %s AND user_id = %s",
            (nova_quantidade,Escolha_epi,user_id)
        )
        db.commit()
        bot.reply_to(quantidade_msg,f"Seu pedido de remoção do item {Escolha_epi} foi realizado com sucesso")
        novamente = 4
        somar_novamente(quantidade_msg,novamente)









#REPETIÇÃO
bot.polling()
