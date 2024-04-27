import config
from vars import all
import dialog
import database
import testsmanager

import os
import telebot
from time import time
import threading



print('imported')

all.bot = telebot.TeleBot(config.bot_key)
# 0[state] 1[last command] 2[selected ege] 3[last time] 4[local test info] 5[test stats] 6[mark up] 7[new]


def update_session(msg):
    id = msg.chat.id
    if id in all.sessions:
        all.sessions[id][2] = time()
        if all.sessions[id][6] != None:
            msg = all.sessions[id][6]
            all.sessions[id][6] = None
            all.bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.id, text=msg.text, reply_markup=None)
        return True
    else:
        print('new user')
        all.sessions[id] = [0, '', time(), 0, None, [0] * 30, None, False]
        database.requests.add((id, 0, msg))
        if all.threaddatalocker.locked():
            all.threaddatalocker.release()
        return False



@all.bot.message_handler(commands=['start'])
def start(msg):
    dialog.sendtemplate('start', msg)

#@all.bot.message_handler(commands=['test'])
def test(msg):
    if msg.chat.id in config.admin_chat_ids:
        database.requests.add((id, 0, None))
        all.threaddatalocker.release()
        print(msg.chat.id) 
        print('end')

@all.bot.message_handler(commands=['help'])
def help(msg):
    dialog.sendtemplate('help', msg)
    
@all.bot.message_handler(commands=['give_test_type'])
def test_by_type(msg):
    a = update_session(msg)
    all.sessions[msg.chat.id][0] = 2
    if a:
        spreader(msg)

@all.bot.message_handler(commands=['give_test_by_nomer'])
def test_by_type(msg):
    a = update_session(msg)
    all.sessions[msg.chat.id][0] = 8
    if a:
        spreader(msg)

@all.bot.message_handler(commands=['stats'])
def statistics(msg):
    print('stats')
    a = update_session(msg)
    if all.sessions[msg.chat.id][7]:
        dialog.sendtemplate('no_data', msg)
        return
    all.sessions[msg.chat.id][0] = 6
    if a:
        spreader(msg)

@all.bot.message_handler(content_types=['text'])
def text(msg):
    a = update_session(msg)
    if all.sessions[msg.chat.id][0] == 0:
        dialog.sendtemplate('what', msg)

    elif all.sessions[msg.chat.id][0] == 3:
        if msg.text is None or not msg.text.isdigit():
            dialog.sendtemplate('uncorrect_nomer', msg)
        else:
            try:
                b = int(msg.text)
            except:
                dialog.sendtemplate('uncorrect_nomer', msg)
                return
            if b > len(all.sessions[msg.chat.id][5]) or b < 1:
                dialog.sendtemplate('uncorrect_nomer', msg)
                return
            all.sessions[msg.chat.id][0] = 4
            testsmanager.requests.add((0, b, all.sessions[msg.chat.id][5][b - 1], msg))
            if all.threadtestslocker.locked():
                all.threadtestslocker.release()

    elif all.sessions[msg.chat.id][0] == 5:
        a = msg.text.strip()
        if a == all.sessions[msg.chat.id][4]['ansver']:
            database.requests.add((msg.chat.id, 2, msg, all.sessions[msg.chat.id][4]['nomer'], True))
            if all.threaddatalocker.locked():
                all.threaddatalocker.release()
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton('подобное', callback_data='test ' + str(all.sessions[msg.chat.id][4]['nomer'])))
            if len(all.sessions[msg.chat.id][4]['solve']) > 5:
                
                markup.add(telebot.types.InlineKeyboardButton('решение', callback_data='solve'))
                
                all.sessions[msg.chat.id][6] = dialog.sendtemplate('truly', msg, mark_up=markup)

            else:
                all.sessions[msg.chat.id][6] = dialog.sendtemplate('truly', msg, mark_up=markup)
                all.sessions[msg.chat.id][4] = None

        else:
            database.requests.add((msg.chat.id, 2, msg, all.sessions[msg.chat.id][4]['nomer'], False))
            if all.threaddatalocker.locked():
                all.threaddatalocker.release()
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton('попробовать ещё', callback_data='test ' + str(all.sessions[msg.chat.id][4]['nomer'])))
            if len(all.sessions[msg.chat.id][4]['solve']) > 5:
                markup.add(telebot.types.InlineKeyboardButton('решение', callback_data='solve'))
                all.sessions[msg.chat.id][6] = dialog.sendtemplate('falsely', msg, extend={'answer': all.sessions[msg.chat.id][4]['ansver']}, mark_up=markup)
            else:
                all.sessions[msg.chat.id][6] = dialog.sendtemplate('falsely', msg, extend={'answer': all.sessions[msg.chat.id][4]['ansver']}, mark_up=markup)
                all.sessions[msg.chat.id][4]= None
            
        all.sessions[msg.chat.id][0] = 0
    elif all.sessions[msg.chat.id][0] == 9:
        if msg.text is None or not msg.text.isdigit():
            dialog.sendtemplate('uncorrect_id', msg)
        else:
            try:
                b = int(msg.text)
            except:
                dialog.sendtemplate('uncorrect_id', msg)
                return
            all.sessions[msg.chat.id][0] = 10
            testsmanager.requests.add((1, b, None, msg))
            if all.threadtestslocker.locked():
                all.threadtestslocker.release()
    else:
        dialog.sendtemplate('loading', msg)
        
        # check for alive

        if not all.threadtestslocker.locked() and time() - all.threadtesttime > 30 and (not all.threadtests.is_alive()):
            print('GENEAL FAILURE!!! thread test not alive!')
            print('trying to restart')
            all.threadtests = threading.Thread(target=testsmanager.thread, daemon=True)
            all.threadtests.start()

        if not all.threaddatalocker.locked() and time() - all.threaddatalasttime > 30 and (not all.threaddata.is_alive()):
            print('GENEAL FAILURE!!! thread data not alive!')
            print('trying to restart')
            all.threaddata = threading.Thread(target=database.thread, daemon=True)
            all.threaddata.start()

            



@all.bot.callback_query_handler(func=lambda x: True)
def callbacks(call):
    if call.message:
        id = call.message.chat.id

        a = update_session(call.message)
        if not a:
            all.bot.edit_message_text(chat_id=id, message_id=call.message.id, text=call.message.text, reply_markup=None)

        if call.data == 'solve':
            if all.sessions[id][4] != None:
                all.bot.send_message(id, all.sessions[id][4]['solve'])
            all.sessions[id][4] = None
        elif call.data == 'percents':
            database.requests.add((id, 3, call.message))
            all.sessions[call.message.chat.id][0] = 7
            if all.threaddatalocker.locked():
                all.threaddatalocker.release()
        elif call.data == 'sums':
            database.requests.add((id, 5, call.message))
            all.sessions[call.message.chat.id][0] = 7
            if all.threaddatalocker.locked():
                all.threaddatalocker.release()
        elif call.data == 'counts':
            database.requests.add((id, 4, call.message))
            all.sessions[call.message.chat.id][0] = 7
            if all.threaddatalocker.locked():
                all.threaddatalocker.release()
        elif 'test' in call.data:
            nom = int(call.data[4:])
            all.sessions[id][0] = 4
            testsmanager.requests.add((0, nom, all.sessions[id][5][nom - 1], call.message))
            if all.threadtestslocker.locked():
                all.threadtestslocker.release()






def statsrdy(pic, msg):
    if all.sessions[msg.chat.id][0] == 7:
        if pic == None:
            dialog.sendtemplate('bad_stats', msg)
            return
        for i in pic:
            all.bot.send_photo(msg.chat.id, i)
        all.sessions[msg.chat.id][0] = 0


def spreader(msg):

    if all.sessions[msg.chat.id][0] == 2:
        all.sessions[msg.chat.id][0] = 3
        dialog.sendtemplate('what_type', msg)
    elif all.sessions[msg.chat.id][0] == 6:
        all.sessions[msg.chat.id][0] = 0
        if all.sessions[msg.chat.id][7]:
            dialog.sendtemplate('no_data', msg)
            return
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton('процент решенных', callback_data='percents'))
        markup.add(telebot.types.InlineKeyboardButton('количество решенных', callback_data='sums'))
        markup.add(telebot.types.InlineKeyboardButton('количество верно/неверно решенных', callback_data='counts'))
        all.sessions[msg.chat.id][6] = dialog.sendtemplate('whatstats', msg, mark_up=markup)
    elif all.sessions[msg.chat.id][0] == 8:
        all.sessions[msg.chat.id][0] = 9
        dialog.sendtemplate('what_id', msg)

def testready(test, msg, info):
    if all.sessions[msg.chat.id][0] == 4 or all.sessions[msg.chat.id][0] == 10:
        if test == None:
            dialog.sendtemplate('no_find', msg)
            all.sessions[msg.chat.id][0] = 0
            return
        else:
            dialog.sendtemplate('test_nomer', msg, extend={'task_id': info[1]})
            all.bot.send_message(msg.chat.id, test['question'])
            for i in test['images']:
                all.bot.send_photo(msg.chat.id, i)
            for i in test['files']:
                all.bot.send_document(msg.chat.id, i)
            all.sessions[msg.chat.id][5][info[0] - 1] = info[1]
            all.sessions[msg.chat.id][0] = 5
            all.sessions[msg.chat.id][4] = test
            database.requests.add((msg.chat.id, 1, msg, info[0]))
            if all.threaddatalocker.locked():
                all.threaddatalocker.release()

    else:
        dialog.sendtemplate('what', msg)



dialog.loadfiles()
testsmanager.load()
all.mainfunc = spreader
all.testrdy = testready
all.statsrdy = statsrdy


all.threaddata = threading.Thread(target=database.thread, daemon=True)
all.threaddatalocker = threading.Lock()
all.threaddialog = threading.Thread(target=dialog.thread, daemon=True)
all.threaddialoglocker = threading.Lock()
all.threadtests = threading.Thread(target=testsmanager.thread, daemon=True)
all.threadtestslocker = threading.Lock()

all.threadtests.start()
all.threaddata.start()
#all.threaddialog.start()

print('starting')
all.bot.polling(none_stop=True)
