import requests
from bs4 import BeautifulSoup 
import json
import base64
import os



def rege(nom):
    res = requests.get("https://math-ege.sdamgia.ru/problem?id=" + str(nom)) 
    sp = BeautifulSoup(res.content, 'html.parser') 
    a = sp.find_all('span')
    flag = False
    for i in a:
        b = i.text
        if 'Тип' in b:
            flag = True

startstr = '"text":"'
endstr = '","key":"'
startsolvestr = '"solve_text":"'
endsolvestr = '","'
def kompege(nom):
    try:
        res = requests.get("https://kompege.ru/api/v1/task/" + str(nom)) 
    except:
        print('exeption download test')
        return False
    if not res.ok:
        print('response not ok')
    if res.text == 'null':
        print('null')
        return False
    jres = res.json()
    if len(jres['text']) < 10:
        print('len of text < 10')
        return False
    if len(jres['key']) < 1:
        print('len of key < 1')
        return False
    if jres['number'] > 100:
        print('number > 100')
        return False
    if jres['number'] == 2:
        print('cannot parse 2 nom')
        return False
    sp = BeautifulSoup(res.content, 'html.parser')
    st = sp.text.find(startstr)
    st += len(startstr)
    end = sp.text.find(endstr)
    if end - st < 10:
        print('result str is to small')
        return False
    resulttext = sp.text[st:end]
    resulttext = resulttext.replace('\\n', '\n', 1000)
    ansver = jres['key']
    st = sp.text.find(startsolvestr)
    st += len(startsolvestr)
    end = sp.text[st:].find(endsolvestr) + st
    ans_text = sp.text[st:end]

    a = sp.find_all('img')
    images = []
    for i in a: ############################# files
        rec = i.get('src')
        if 'data:' not in rec[:8]:
            rec = rec[2:-2]
            try:
                res = requests.get(rec)
            except:
                print('exeption on download Image')
                return False

            if not res.ok:
                continue
            print('load image', rec)
            rec = rec[rec.rfind('/') + 1:]
            out = res.content
        else:
            print('bad image')
            
            out = (rec[rec.find(',') + 1:])
            
            out = base64.b64decode(out)
            rec = str(jres['number']) + '-' + str(nom) + '.png'

        if rec in images:
            print('images dublication')
            continue
        f = open('tests/inf/images/' + rec, 'wb')
        f.write(out)
        f.close()
        images.append(rec)

    files = []
    name = str(jres['number']) + '-' + str(nom)
    for i in jres['files']:
        rec = 'https://kompege.ru' + i['url']
        try:
            res = requests.get(rec)
        except:
            print('exeption on download file')
            return False
        if not res.ok:
            continue
        print('load file', rec)
        if name + '-' + i['name'] in files:
            print('file dublication')
            continue
        f = open('tests/inf/files/' + name + '-' + i['name'], 'wb')
        f.write(res.content)
        f.close()
        files.append(name + '-' + i['name'])
    record = {'question': resulttext, 'ansver': ansver, 'solve': ans_text, 'files': files, 'images': images}
    a = str(jres['number']) + '-' + str(nom)
    print(record['question'])
    print('saved', a)
    f = open('tests/inf/tests/' + a + '.json', 'w')
    json.dump(record, f)
    f.close()
    return True

def findmins():
    files = os.listdir('tests/inf/tests')
    print(files)
    minnoms = [1000000] * 30
    for i in files:
        if not os.path.isfile('tests/inf/tests/' + i):
            continue
        a, b = i.split('-')
        b, _ = b.split('.')
        a, b = int(a), int(b)
        print(b)
        minnoms[a - 1] = min(minnoms[a - 1], b)
    f = open('tests/inf/info.txt', 'w')
    for i in range(len(minnoms)):
        if minnoms[i] == 1000000:
            a = 0
        else:
            a = minnoms[i]
        f.write(str(i + 1) + ' ' + str(a))
        f.write('\n')
    f.close()

kompege(14405)
kompege(15313)

exit()
for i in range(12780, 13000):
    try:
        if kompege(i):
            print('saved', i)
    except:
        print('GLOBAL EXEPTION!!!')
findmins()

