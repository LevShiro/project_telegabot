from vars import all
import sqlite3

requests = set()


def thread():
    load()
    while True:
        
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
                        all.sessions[a[0]][5][i - 1] = res[i]
                    
                if a[2] != None:
                    all.mainfunc(a[2])    
            if a[1] == 1: #0[id] 1[type] 2[msg] 3[task nom]
                st = 'n' + str(a[3])
                if not all.sessions[a[0]][7]:
                    all.cur.execute(f"""UPDATE info SET {st} = {all.sessions[a[0]][5][a[3] - 1]} WHERE id = {a[0]}""")
                    
                else:
                    all.cur.execute(f"""INSERT INTO info(id, {st}) VALUES({a[0]}, {all.sessions[a[0]][5][a[3] - 1]})""")
                    st = ', 0' * 60
                    st2 = ''
                    for i in range(30):
                        st2 += ', T' + str(i + 1)
                        st2 += ', F' + str(i + 1)
                    all.cur.execute(f"""INSERT INTO stats(id{st2}) VALUES({a[0]}{st})""")
                    all.sessions[a[0]][7] = False
                    print('add new info')
            if a[1] == 2:#0[id] 1[type] 2[msg] 3[task nom] 4[true or false]
                print('saving', a[0], 'stats')
                if a[4]:
                    st = 'T' + str(a[3])
                else:
                    st = 'F' + str(a[3])
                all.cur.execute(f"""UPDATE stats SET {st} = ({st} + 1) WHERE id = {a[0]}""")

                


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
