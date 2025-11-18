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

#AUTORIZADOS A MEXER EM REMOÇÃO E ADIÇÃO
Autorizados = {5007489215}

#INCIO DO CODIGO
@bot.message_handler(commands=['salvar'])
def save_note(msg):
    user_id = msg.from_user.id
    parts = msg.text.split(maxsplit=1)
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
     bot.reply_to(msg,f"Salvo '{text_to_save}'")
    except Exception as e:
     bot.reply_to(msg, f"Erro ao salvar no banco: {e}")
    else:
        bot.reply_to(msg, "Use /salvar <texto para salvar>")

#INICIO DA CHAMADA DO BOT
@bot.message_handler(func=lambda message: True)
def primeira_pergunta_bot(msg):
    chat_id = msg.chat.id
    #Adição de botões
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    btn1 = types.KeyboardButton("Consultas")
    btn2 = types.KeyboardButton("Adicionar ao estoque")
    btn3 = types.KeyboardButton("Remover do estoque")
    markup.add(btn1,btn2,btn3)

    #Inicio da interface do usuario
    bot.reply_to(msg,"Bem-vindo às consultas da Fazenda" )
    msg = bot.send_message(chat_id,"Escolha uma opção:\n" \
    " Consultas \n\n" \
    " Adicionar ao estoque \n\n" \
    " Remover do estoque",reply_markup=markup)
    #Mandando a mensagem salva para a proxima função
    bot.register_next_step_handler(msg,escolha_de_avanço)

def escolha_de_avanço(msg):
    texto = msg.text
    chat_id = msg.chat.id
    user_id = msg.from_user.id

    if texto == "Consultas":
        #Adição dos botões
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        btn1 = types.KeyboardButton("EPI")
        btn2 = types.KeyboardButton("Fertilizantes")
        btn3 = types.KeyboardButton("Voltar")
        markup.add(btn1,btn2,btn3)

        #Interface do usuario
        bot.reply_to(msg,"Você está entrando nas consultas.\n")
        msg_consulta = bot.send_message(chat_id,"O que deseja consultar?\n" \
      " EPI \n\n" \
      " Fertilizantes\n\n" \
      " Voltar",reply_markup=markup)
        
        #Mandando a mensagem salva para a proxima função
        bot.register_next_step_handler(msg_consulta, escolha_de_qual_consulta)
        
    elif texto == "Adicionar ao estoque":

        if user_id not in Autorizados:
            bot.reply_to(msg, "⚠️ Você não tem permissão para adicionar itens ao estoque.")
            primeira_pergunta_bot(msg)
        else:
            #Adição dos botões
            markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
            btn1 = types.KeyboardButton("EPI")
            btn2 = types.KeyboardButton("Fertilizantes")
            btn3 = types.KeyboardButton("Voltar")
            markup.add(btn1,btn2,btn3)

            #Interface do usuario
            bot.reply_to(msg,"Você está entrando na adição ao estoque.\n")
            msg_compra = bot.send_message(chat_id,"O que deseja adicionar ao estoque?\n" \
            " EPI \n\n" \
            " Fertilizantes\n\n" \
            " Voltar",reply_markup=markup)

            #Mandando a mensagem salva para a proxima função
            bot.register_next_step_handler(msg_compra, escolha_adiçao_do_estoque)

    elif texto == "Remover do estoque":

        if user_id not in Autorizados:
            # Corrigi a mensagem aqui pois o usuario clicou em remover, mas o aviso falava "adicionar"
            bot.reply_to(msg, "⚠️ Você não tem permissão para remover itens do estoque.")
            escolha_de_avanço(msg)
        else:
            #Adição dos botões
            markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
            btn1 = types.KeyboardButton("EPI")
            btn2 = types.KeyboardButton("Fertilizantes")
            btn3 = types.KeyboardButton("Voltar")
            markup.add(btn1,btn2,btn3)

            #Interface do usuario
            bot.reply_to(msg,"Você está entrando na remoção de produtos do estoque.")
            msg_compra = bot.send_message(chat_id,"O que deseja remover do estoque?\n\n"
            " EPI \n\n" \
            " Fertilizantes\n\n" \
            " Voltar",reply_markup=markup)

            #Mandando a mensagem salva para a proxima função
            bot.register_next_step_handler(msg_compra,escolha_remover_estoque)

def escolha_de_qual_consulta(msg):
    escolha = msg.text
    if escolha == "EPI":
        bot.reply_to(msg,"Você está entrando na consulta de EPIs.")
        consulta_epi(msg)
    elif escolha =="Fertilizantes":
        bot.reply_to(msg,"Você está entrando na consulta de Fertilizantes.")
        consulta_fertilizante(msg)
    elif escolha =="Voltar":
        bot.reply_to(msg,"Você está voltando ao menu principal.")
        primeira_pergunta_bot(msg)

def escolha_adiçao_do_estoque(msg):
    escolha = msg.text
    if escolha == "EPI":
        escolha1 = "adição"
        bot.reply_to(msg,"Você está entrando na adição de estoque de EPIs.")
        registro_epi(msg,escolha1)
    elif escolha =="Fertilizantes":
        escolha1 = "adição"
        bot.reply_to(msg,"Você está entrando na adição de estoque de Fertilizantes.")
        registro_fertilizante(msg,escolha1)
    elif escolha =="Voltar":
        bot.reply_to(msg,"Você está voltando ao menu principal.")
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
        bot.reply_to(msg,"Você está voltando ao menu principal.")
        primeira_pergunta_bot(msg)

def processar_somar_e_remover_novamente(msg,novamente):
    if novamente in (1,3):
        #Adição dos botões
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        btn1 = types.KeyboardButton("Sim")
        btn2 = types.KeyboardButton("Não")
        markup.add(btn1,btn2)
        #Interface do usuario
        somar_ou_remover_ou_consultar_novamente = bot.reply_to(msg,"Deseja adicionar algo mais ao estoque?",reply_markup=markup)
        bot.register_next_step_handler(msg,somar_e_remover_e_consultar_novamente,novamente,somar_ou_remover_ou_consultar_novamente)
    elif novamente in (2,4):
        #Adição dos botões
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        btn1 = types.KeyboardButton("Sim")
        btn2 = types.KeyboardButton("Não")
        markup.add(btn1,btn2)
        #Interface do usuario
        somar_ou_remover_ou_consultar_novamente = bot.reply_to(msg,"Deseja remover algo mais do estoque?",reply_markup=markup)
        bot.register_next_step_handler(msg,somar_e_remover_e_consultar_novamente,novamente,somar_ou_remover_ou_consultar_novamente)
    elif novamente in (5,6):
        #Adição dos botões
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        btn1 = types.KeyboardButton("Sim")
        btn2 = types.KeyboardButton("Não")
        markup.add(btn1,btn2)
        #Interface do usuario
        somar_ou_remover_ou_consultar_novamente = bot.reply_to(msg,"Deseja consultar algo mais?",reply_markup=markup)
        bot.register_next_step_handler(msg,somar_e_remover_e_consultar_novamente,novamente,somar_ou_remover_ou_consultar_novamente)    

def somar_e_remover_e_consultar_novamente(msg,novamente,somar_ou_remover_ou_consultar_novamente):
    #Soma novamente Fertilizante
    if novamente == 1:
        somar_ou_remover_ou_consultar_novamente = msg.text
        if somar_ou_remover_ou_consultar_novamente == "Sim":
            escolha1 = "adição"
            registro_fertilizante(msg,escolha1)
        elif somar_ou_remover_ou_consultar_novamente == "Não" : 
            primeira_pergunta_bot(msg)
    #Remove novamente Fertilizante
    elif novamente == 2:
        somar_ou_remover_ou_consultar_novamente = msg.text
        if somar_ou_remover_ou_consultar_novamente == "Sim":
            escolha1 = "remoção"
            registro_fertilizante(msg,escolha1)
        elif somar_ou_remover_ou_consultar_novamente == "Não": 
            primeira_pergunta_bot(msg)
    #Soma novamente EPI
    elif novamente == 3:
        somar_ou_remover_ou_consultar_novamente = msg.text
        if somar_ou_remover_ou_consultar_novamente == "Sim":
            escolha1 = "adição"
            registro_epi(msg,escolha1)
        elif somar_ou_remover_ou_consultar_novamente == "Não" : 
            primeira_pergunta_bot(msg)
    #Remove novamente EPI
    elif novamente == 4:
        somar_ou_remover_ou_consultar_novamente = msg.text
        if somar_ou_remover_ou_consultar_novamente == "Sim":
            escolha1 = "remoção"
            registro_epi(msg,escolha1)
        elif somar_ou_remover_ou_consultar_novamente == "Não": 
            primeira_pergunta_bot(msg)
    #Consulta Fertilizante
    elif novamente == 5:
        if somar_ou_remover_ou_consultar_novamente == "Sim":
            escolha_consulta = "EPI"
            escolha_de_qual_consulta(escolha_consulta)
        elif somar_ou_remover_ou_consultar_novamente == "Não": 
            primeira_pergunta_bot(msg)
    #Consulta EPI
    elif novamente == 6:
        if somar_ou_remover_ou_consultar_novamente == "Sim":
            escolha_de_qual_consulta(msg)
        elif somar_ou_remover_ou_consultar_novamente == "Não": 
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
    novamente = 5
    processar_somar_e_remover_novamente(msg,novamente)

def registro_fertilizante(msg,escolha1):
    global db, cursor
    user_id = str(msg.from_user.id)
    #Adição de botões
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    btn1 = types.KeyboardButton("Adubo")
    btn2 = types.KeyboardButton("Voltar")
    markup.add(btn1,btn2)

    bot.reply_to(msg,"Escolha uma opção: \n" \
    " Adubo\n\n" \
    " Voltar\n\n",reply_markup=markup)
    bot.register_next_step_handler(msg, quantidade_fertilizante, escolha1,user_id)      

def quantidade_fertilizante(msg,escolha1,user_id):
    global db, cursor
    Escolha_fertilizante = msg.text.strip() 

    if Escolha_fertilizante =="Voltar":
        bot.reply_to(msg,"Você está voltando ao menu principal.")
        primeira_pergunta_bot(msg)

    else:
        if escolha1 == "adição":
            msg_enviada = bot.reply_to(msg,"Qual a quantidade você deseja adicionar ao estoque?")
            bot.register_next_step_handler(msg_enviada,somar_produto_fertilizante,Escolha_fertilizante,user_id)
        elif escolha1 == "remoção":
            msg_enviada = bot.reply_to(msg,"Qual a quantidade você deseja remover do estoque?")
            bot.register_next_step_handler(msg_enviada,remover_produto_fertilizante,Escolha_fertilizante,user_id)

def somar_produto_fertilizante(msg,Escolha_fertilizante,user_id):
    global db, cursor
    print("Chegou ate aqui normal")
    quantidade = int(msg.text.strip())
    

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
    bot.reply_to(msg,f"Seu pedido de adição do item {Escolha_fertilizante} foi realizado com sucesso.")
    novamente = 1
    processar_somar_e_remover_novamente(msg,novamente)

def remover_produto_fertilizante(msg,Escolha_fertilizante,user_id):
    global db, cursor
    quantidade = int(msg.text.strip())

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
        bot.reply_to(msg,"O estoque não pode ficar negativo. Tente outro valor.")
        escolha1 = "remoção"
        bot.register_next_step_handler(msg,remover_produto_fertilizante,Escolha_fertilizante,user_id)
    else:
        print("começou a atualizar")    
        cursor.execute(
            "UPDATE soma_fertilizante SET quantidade_em_sacos = %s WHERE  categoria_item = %s AND user_id = %s",
            (nova_quantidade,Escolha_fertilizante,user_id)
        )
        db.commit()
        bot.reply_to(msg,f"Seu pedido de remoção do item {Escolha_fertilizante} foi realizado com sucesso.")
        novamente = 2
        processar_somar_e_remover_novamente(msg,novamente)

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
    novamente = 6
    processar_somar_e_remover_novamente(msg,novamente)

def registro_epi(msg,escolha1):
    global db, cursor
    user_id = str(msg.from_user.id)
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
    bot.reply_to(msg,"Escolha um EPI: \n" \
    " Capacete\n" \
    " Luva \n" \
    " Butina\n" \
    " Protetor auricular\n" \
    " Oculos\n" \
    "\nVoltar",reply_markup=markup)

    #Mandando a mensagem salva para a proxima função
    bot.register_next_step_handler(msg, quantidade_epi,escolha1, user_id) 
    
def quantidade_epi(msg,escolha1,user_id):
    global db, cursor
    Escolha_epi = msg.text
    if Escolha_epi =="Voltar":
        bot.reply_to(msg,"Você está voltando ao menu principal.")
        primeira_pergunta_bot(msg)
    else:
        if escolha1 == "adição":
            Escolha_epi = msg.text 
            msg_enviada = bot.reply_to(msg,"Qual a quantidade você deseja adicionar ao estoque?")
            bot.register_next_step_handler(msg_enviada,somar_produto_epi,Escolha_epi,user_id)
        elif escolha1 == "remoção":
            Escolha_epi = msg.text 
            msg_enviada = bot.reply_to(msg,"Qual a quantidade você deseja remover do estoque?")
            bot.register_next_step_handler(msg_enviada,remover_produto_epi,Escolha_epi,user_id)

def somar_produto_epi(msg,Escolha_epi,user_id):
    global db, cursor
    quantidade = int(msg.text.strip())

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
    bot.reply_to(msg,f"Seu pedido de adição do item {Escolha_epi} foi realizado com sucesso.")
    novamente = 3
    processar_somar_e_remover_novamente(msg,novamente)
    
def remover_produto_epi(msg,Escolha_epi,user_id):
    global db, cursor
    quantidade = int(msg.text.strip())

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
        bot.reply_to(msg,"O estoque não pode ficar negativo. Tente outro valor.")
        escolha1 = "remoção"
        bot.register_next_step_handler(msg,remover_produto_epi,Escolha_epi,user_id)
    else:
        cursor.execute(
            "UPDATE pedidos_compras SET quantidade = %s WHERE  categoria_item = %s AND user_id = %s",
            (nova_quantidade,Escolha_epi,user_id)
        )
        db.commit()
        bot.reply_to(msg,f"Seu pedido de remoção do item {Escolha_epi} foi realizado com sucesso.")
        novamente = 4
        processar_somar_e_remover_novamente(msg,novamente)

#REPETIÇÃO
bot.polling()