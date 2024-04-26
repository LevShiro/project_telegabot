from vars import all
import os
import json


infnoms = []
# 0[type] 1[nomer] 2[pref nom] 3[msg]
requests = set()

def thread():
    
    while True:
        if len(requests) < 1:
            all.threadtestslocker.acquire()
        else:
            a = requests.pop()
            if a[0] == 0:
                if 0 > a[1] - 1 >= len(infnoms):
                    all.testrdy(None, a[3])
                    continue
                if len(infnoms[a[1] - 1]) < 1:
                    all.testrdy(None, a[3])
                    continue
                b = 100000000
                for i, j in infnoms[a[1] - 1].items():
                    if i > a[2]:
                        b = i
                        break
                    b = min(b, i)
                f = open('tests/inf/tests/' + infnoms[a[1] - 1][b])
                res = json.load(f)
                f.close()
                for i in range(len(res['files'])):
                    try:
                        f = open('tests/inf/files/' + res['files'][i], 'rb')
                    except:
                        all.testrdy(None, a[3])
                        continue
                    res['files'][i] = f 

                for i in range(len(res['images'])):
                    try:
                        f = open('tests/inf/images/' + res['images'][i], 'rb')
                    except:
                        all.testrdy(None, a[3])
                        continue
                    res['images'][i] = f.read()
                    f.close()
                all.testrdy(res, a[3], (a[1], b))
                continue



        print('tests working')



def load():
    for i in range(30):
        infnoms.append({})
    files = os.listdir('tests/inf/tests')
    for name in files:
        i = name[:name.find('.')]
        a = i.split('-')
        if len(a) < 2:
            continue
        a, b = int(a[0]), int(a[1])
        if a > 29:
            continue
        infnoms[a - 1][b] = name

    print('loaded', len(files))

