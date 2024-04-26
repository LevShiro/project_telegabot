from vars import all
import sqlite3

requests = set()


def thread():
    load()
    while True:
        print('data working')
        if len(requests) < 1:
            all.threaddatalocker.acquire()
        else: 
            a = requests.pop()
            if a[1] == 0:
                res = all.cur.execute(f"""SELECT * FROM info WHERE id == {a[0]}""").fetchone()
                if not res == None:
                    pass
                all.mainfunc(a[2])    
                
            print(res)


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
