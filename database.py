from vars import all
import sqlite3
import requests as rq
from time import time

requests = set()

solpercent = 'процент решения'
truly = 'верные'
falsely = 'неверные'
colsmakes = 'количество решенных'

labels1 = []
labels2 = []

def thread():
    load()
    print('starting thread database')
    while True:
        all.threaddatalasttime = time()

        if len(requests) < 1:
            all.con.commit()
            all.threaddatalocker.acquire()
        else: 
            a = requests.pop()
            if a[1] == 0:
                res = all.cur.execute(f"""SELECT * FROM info WHERE id == {a[0]}""").fetchone()
                if res == None:
                    all.sessions[a[0]][7] = True
                else:
                    for i in range(1, len(res)):
                        if res[i] != None:
                            all.sessions[a[0]][5][i - 1] = res[i]
                    
                if a[2] != None:
                    all.mainfunc(a[2])    
            elif a[1] == 1: #0[id] 1[type] 2[msg] 3[task nom]
                st = 'n' + str(a[3])
                if not all.sessions[a[0]][7]:
                    all.cur.execute(f"""UPDATE info SET {st} = {all.sessions[a[0]][5][a[3] - 1]} WHERE id = {a[0]}""")
                    
                else:
                    res = all.cur.execute(f"""SELECT * FROM info WHERE id == {a[0]}""").fetchone()
                    all.sessions[a[0]][7] = False
                    if res != None:
                        continue

                    all.cur.execute(f"""INSERT INTO info(id, {st}) VALUES({a[0]}, {all.sessions[a[0]][5][a[3] - 1]})""")
                    st = ', 0' * 60
                    st2 = ''
                    for i in range(30):
                        st2 += ', T' + str(i + 1)
                        st2 += ', F' + str(i + 1)
                    all.cur.execute(f"""INSERT INTO stats(id{st2}) VALUES({a[0]}{st})""")
                    
                    print('add new info')
            if a[1] == 2:#0[id] 1[type] 2[msg] 3[task nom] 4[true or false]
                print('saving', a[0], 'stats')
                if a[4]:
                    st = 'T' + str(a[3])
                else:
                    st = 'F' + str(a[3])
                all.cur.execute(f"""UPDATE stats SET {st} = ({st} + 1) WHERE id = {a[0]}""")
            elif a[1] == 3:
                print('making stats perc')
                res = all.cur.execute(f"""SELECT * FROM stats WHERE id == {a[0]}""").fetchone()
                if res == None:
                    all.sessions[a[0]][7] = False
                    if a[2] != None:
                        all.statsrdy(None, a[2])
                        continue
                rec = {'type':'bar',
                       'data':{'labels': labels1,
                            'datasets': [{'label':solpercent, 'data':[]}]}}
                
                
                mas1 = []
                mas2 = []
                for i in range(13):
                    if (res[i * 2 + 1] + res[i * 2 + 2]) != 0:
                        mas1.append(round(res[i * 2 + 1] / (res[i * 2 + 1] + res[i * 2 + 2]), 2) * 100)
                for i in range(13, 27):
                    if (res[i * 2 + 1] + res[i * 2 + 2]) != 0:
                        mas2.append(round(res[i * 2 + 1] / (res[i * 2 + 1] + res[i * 2 + 2]), 2) * 100) 

                rec['data']['datasets'][0]['data'] = mas1
                result1 = rq.get(all.chartimgsAPI + str(rec))

                rec['data']['labels'] = labels2
                rec['data']['datasets'][0]['data'] = mas2
                result2 = rq.get(all.chartimgsAPI + str(rec))

                if (not result1.ok) or (not result2.ok):
                    all.statsrdy(None, a[2])
                    continue
                print('stats ready')
                all.statsrdy((result1.content, result2.content), a[2])



            elif a[1] == 4:

                print('making stats counts true false')
                res = all.cur.execute(f"""SELECT * FROM stats WHERE id == {a[0]}""").fetchone()
                if res == None:
                    all.sessions[a[0]][7] = False
                    if a[2] != None:
                        all.statsrdy(None, a[2])
                        continue

                rec = {'type':'bar',
                       'data':{'labels': labels1,
                            'datasets': [{'label': truly, 'data':[], 'backgroundColor': 'rgb(75, 192, 75)'},
                                         {'label': falsely, 'data':[], 'backgroundColor': 'rgb(255, 99, 132)'}]}}
                mas1 = []
                mas2 = []
                for i in range(13):
                    mas1.append(res[i * 2 + 1])

                for i in range(13):
                    mas2.append(res[i * 2 + 2]) 

                rec['data']['datasets'][0]['data'] = mas1
                rec['data']['datasets'][1]['data'] = mas2
                result1 = rq.get(all.chartimgsAPI + str(rec))
                if not result1.ok:
                    all.statsrdy(None, a[2])
                    continue

                mas1 = []
                mas2 = []
                for i in range(13, 27):
                    mas1.append(res[i * 2 + 1])

                for i in range(13, 27):
                    mas2.append(res[i * 2 + 2]) 

                rec['data']['labels'] = labels2
                rec['data']['datasets'][0]['data'] = mas1
                rec['data']['datasets'][1]['data'] = mas2
                result2 = rq.get(all.chartimgsAPI + str(rec))

                if (not result1.ok) or (not result2.ok):
                    all.statsrdy(None, a[2])
                    continue
                print('stats ready')
                all.statsrdy((result1.content, result2.content), a[2])


            elif a[1] == 5:
                print('making stats counts')
                res = all.cur.execute(f"""SELECT * FROM stats WHERE id == {a[0]}""").fetchone()
                if res == None:
                    all.sessions[a[0]][7] = False
                    if a[2] != None:
                        all.statsrdy(None, a[2])
                        continue
                rec = {'type':'bar',
                       'data':{'labels': labels1,
                            'datasets': [{'label':colsmakes, 'data':[]}]}}
                
                
                mas1 = []
                mas2 = []
                for i in range(13):
                    if (res[i * 2 + 1] + res[i * 2 + 2]) != 0:
                        mas1.append(res[i * 2 + 1] + res[i * 2 + 2])
                for i in range(13, 27):
                    mas2.append(res[i * 2 + 1] + res[i * 2 + 2]) 

                rec['data']['datasets'][0]['data'] = mas1
                result1 = rq.get(all.chartimgsAPI + str(rec))
                if not result1.ok:
                    all.statsrdy(None, a[2])
                    continue

                rec['data']['labels'] = labels2
                rec['data']['datasets'][0]['data'] = mas2
                result2 = rq.get(all.chartimgsAPI + str(rec))

                if (not result1.ok) or (not result2.ok):
                    all.statsrdy(None, a[2])
                    continue
                print('stats ready')
                all.statsrdy((result1.content, result2.content), a[2])
            elif a[1] == 6:
                if len(a) > 2000:
                    a = max(all.sessions, key=lambda x: abs(time() - all.sessions[x][3]) - 1000 * all.sessions[x][0])
                    if a in all.sessions:
                        del all.sessions[a]


                


def load():
    all.con = sqlite3.connect("tests\inf\data.sqlite")
    all.cur = all.con.cursor()
    try:
        all.cur.execute("""SELECT * FROM info""")
    except:
        print('table info not found, creating info table')
        a = """CREATE TABLE info(id INT"""
        for i in range(30):
            b = ', n' + str(i + 1) + ' INT'
            a += b
        a += ')'
        all.cur.execute(a)

    try:
        all.cur.execute("""SELECT * FROM stats""")
    except:
        print('table stats not found, creating stats table')
        a = """CREATE TABLE stats(id INT"""
        for i in range(30):
            b = ', T' + str(i + 1) + ' INT'
            a += b
            b = ', F' + str(i + 1) + ' INT'
            a += b
        a += ')'
        all.cur.execute(a)
    for i in range(13):
        labels1.append(str(i + 1))
    for i in range(13, 27):
        labels2.append(str(i + 1))
