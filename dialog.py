from vars import all
import os
# (type, name)
# 0 - text
# 1 - img
templates = {'start': [[], 'templates/welcome.txt', 1],
             'help': [[], 'templates/help.txt', 1],
             'what_type': [[], 'templates/what_type.txt', 1],
             'uncorrect_nomer': [[], 'templates/unncorrect.txt', 1],
             'loading': [[], 'templates/please_wait.txt', 1],
             'no_find': [[], 'templates/no found.txt', 1],
             'what': [[], 'templates/what.txt', 1],
             'truly': [[], 'templates/sucses.txt', 1],
             'falsely': [[], 'templates/no sucsess.txt', 1],
             'empty': [[(0, '')], 'templates/empty.txt', 1]
    }

data = {}
requests = set()


def loadfiles():
    print('loading files')
    for i, j in templates.items():
        if not os.path.isfile(templates[i][1]):
            print('cant open file', templates[i][1])
            continue
        print('load file', templates[i][1])
        f = open(templates[i][1], encoding='utf-8')
        a = ''
        for st in f:
            
            if st[:4] == '/img':
                if a != '':
                    templates[i][0].append((0, a))
                a = st.split()
                if len(a) > 1:
                    if os.path.isfile(a[1]):
                        a = open(a[1], 'rb')
                        templates[i][0].append((1, a.read()))
                        a.close()
                    else:
                        print('cant find image', a[1])
                a = ''
            else:
                a += st
        if a != '':
            templates[i][0].append((0, a))
        f.close()

def thread():

    while True:
        if len(requests) < 1:
            all.threaddialoglocker.acquire()
            print(len(requests))
        else:
            a = requests.pop()
            unparalel_sendtemplate(a[0], a[1], extend=a[2], usedef=a[3])  


def sendtemplate(template, msg, extend={}, usedef=True, mark_up=None):

    for i in templates[template][0]:
        if i[0] == 0:
            if usedef:
                ls_id = all.bot.send_message(msg.chat.id,
                                    i[1].format(**data, **{'user_name': msg.from_user.first_name,
                                                            'user_second_name': msg.from_user.last_name}, **extend),
                                    reply_markup=mark_up)
            else:
                all.bot.send_message(msg.chat.id, **extend)
        elif i[0] == 1:
            all.bot.send_photo(msg.chat.id, i[1])
    return ls_id


def paralel_sendtemplate(template, msg, extend={}, usedef=True):
    a = (template, msg, extend, usedef)
    print(type(a))

    requests.add(a)
    if all.threaddialoglocker.locked:
        all.threaddialoglocker.release()

def unparalel_sendtemplate(template, msg, extend={}, usedef=True):
    pass