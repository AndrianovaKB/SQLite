import os
import sqlite3 as sq
import pandas as pd

def remove_gaps(s):
    """Удаление пробелов"""
    return s.strip()

def vuz_name():
    with sq.connect('VUZ.sqlite') as con:
        cur = con.cursor()
        district = cur.execute('SELECT DISTINCT region FROM vuzkart;').fetchall()
        district = [x[0] for x in district]
        district = list(map(remove_gaps, district))
        print('Выберите федеральный округ:')
        for row in district:
            print(row)
        while True:
            federal_district = remove_gaps(input('\n Выберите округ:'))
            if federal_district in district:
                break
            else:
                print('Данный федеральный округ не представлен в списке')
        federal_district = federal_district + '%'
        cur.execute('SELECT z1 FROM vuzkart WHERE region LIKE ? AND www!=0;',[federal_district])
        vuz = cur.fetchall()
        vuz = [x[0] for x in vuz]
        print('Список вузов:')
        for row in vuz:
            print(row)

def students():
    con = sq.connect('VUZ.sqlite')
    cur = con.cursor()
    city_ = cur.execute('SELECT DISTINCT city FROM vuzkart;').fetchall()
    city_ = [x[0] for x in city_]
    city_.append('Все')
    city_ = list(map(remove_gaps, city_))
    print('Выберите город:')
    for row in city_:
        print(row)
    while True:
        CITY = remove_gaps(input('\n Выберите город:'))
        if CITY in city_:
            break
        else:
            print('Данный город не представлен в списке')
    all_cities = cur.execute('SELECT city FROM vuzkart;')
    all_cities = cur.fetchall()
    all_cities = [x[0] for x in all_cities]
    all_cities = list(map(remove_gaps, all_cities))
    bac = cur.execute('SELECT BAC FROM vuzstat;')
    bac = cur.fetchall()
    bac = [x[0] for x in bac]
    spec = cur.execute('SELECT SPEC FROM vuzstat;')
    spec = cur.fetchall()
    spec = [x[0] for x in spec]
    mag = cur.execute('SELECT MAG FROM vuzstat;')
    mag = cur.fetchall()
    mag = [x[0] for x in mag]
    stud = cur.execute('SELECT STUD FROM vuzstat;')
    stud = cur.fetchall()
    stud = [x[0] for x in stud]
    
    bac_sum = [0]*len(city_)
    spec_sum = [0]*len(city_)
    mag_sum = [0]*len(city_)
    percent_bac = [0]*len(city_)
    percent_spec = [0]*len(city_)
    percent_mag = [0]*len(city_)
    stud_sum = [0]*len(city_)
    for j in range(len(city_)):
        for i in range(len(all_cities)):
            if all_cities[i] == city_[j]:
                bac_sum[j] += bac[i]
                spec_sum[j] += spec[i]
                mag_sum[j] += mag[i]
                stud_sum[j] += stud[i]
        if stud_sum[j] == 0:
            break
        else:
            percent_bac[j] = round(bac_sum[j]/stud_sum[j]*100,3)
            percent_spec[j] = round(spec_sum[j]/stud_sum[j]*100,3)
            percent_mag[j] = round(mag_sum[j]/stud_sum[j]*100,3)
    k = 3*len(city_)
    percent_ = []
    count = []
    for j in range(len(city_)):
        percent_.append(percent_bac[j])
        percent_.append(percent_spec[j])
        percent_.append(percent_mag[j])
        count.append(bac_sum[j])
        count.append(spec_sum[j])
        count.append(mag_sum[j])
    level = ['бакалавриат  ','специалитет ','магистратура']
    level = level*k
    city1_ = []
    for i in city_:
        city1_.extend([i]*3)
    
    with sq.connect('level_of_education_bd.sqlite') as con:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS level_of_education_bd(
            number INTEGER, city TEXT, level_of_education TEXT, amount INTEGER, percent REAL
            )""")
        for i in range(k):
            cur.execute("""INSERT INTO level_of_education_bd(number, city, level_of_education,
                    amount, percent) VALUES(?,?,?,?,?);""",
                        (i+1, city1_[i], level[i], count[i], percent_[i]))
        cur.execute("""INSERT INTO level_of_education_bd(number, city, level_of_education,
                    amount, percent) VALUES(?,?,?,?,?)""",
                    ('', '', 'Все', sum(stud), ''))
        if CITY == 'Все':
            summ = [sum(bac_sum), sum(spec_sum), sum(mag_sum)]
            proc_bac = round(sum(bac_sum)/sum(stud_sum)*100,3)
            proc_spec = round(sum(spec_sum)/sum(stud_sum)*100,3)
            proc_mag = round(sum(mag_sum)/sum(stud_sum)*100,3)
            proc = [proc_bac, proc_spec, proc_mag]
            lv = ['бакалавриат  ','специалитет ','магистратура']
            print('номер', 'уровень подготовки', 'количество студентов', 'процент')
            a=0
            for a in range(3):
                print('  ',a+1,' '*4, lv[a],' '*9, summ[a],' '*5, proc[a])
            print(' '*9, 'Все',' '*17, sum(stud_sum))
        else:
            cur.execute("""SELECT level_of_education FROM level_of_education_bd
                         WHERE city = ?;""",[CITY])
            lv1 = cur.fetchall()
            cur.execute("""SELECT amount FROM level_of_education_bd
                         WHERE city = ?;""",[CITY])
            lv2 = cur.fetchall()
            cur.execute("""SELECT percent FROM level_of_education_bd
                         WHERE city = ?;""",[CITY])
            lv3 = cur.fetchall()
            lv1 = [x[0] for x in lv1]
            lv2 = [x[0] for x in lv2]
            lv3 = [x[0] for x in lv3]
            a = 0
            print('номер', 'уровень подготовки', 'количество студентов', 'процент')
            for a in range(3):
                print('  ',a+1,' '*5,lv1[a],' '*8,lv2[a],' '*7,lv3[a])
            print(' '*10, 'Все',' '*17, lv2[0]+lv2[1]+lv2[2])
             
def Vuzkart():
    """Вывод таблицы Vuzkart"""
    con = sq.connect('VUZ.sqlite')
    cur = con.cursor()
    sql ='SELECT * FROM vuzkart'
    cur.execute(sql)
    polya_BD = cur.description
    sod_BD = cur.execute(sql).fetchall()
    cur.close()
    con.close()
    print("""|{:^8}|{:^200}|{:^250}|{:^12}|{:^100}|{:^12}|{:^110}|
        {:^40}|{:^20}|{:^30}|{:^30}|{:^40}|{:^17}|{:^20}|{:^15}|{:^40}|
        {:^7}|{:^5}|""".format(polya_BD[0][0], polya_BD[1][0], polya_BD[2][0],
        polya_BD[3][0], polya_BD[4][0], polya_BD[5][0], polya_BD[6][0],
        polya_BD[7][0], polya_BD[8][0], polya_BD[9][0], polya_BD[10][0],
        polya_BD[11][0], polya_BD[12][0], polya_BD[13][0], polya_BD[14][0],
        polya_BD[15][0], polya_BD[16][0], polya_BD[17][0]))
    for i in range(len(sod_BD)):
        print(f"""|{remove_gaps(sod_BD[i][0]):^8}|{remove_gaps(sod_BD[i][1]):^200}|
              {remove_gaps(sod_BD[i][2]):^250}|{sod_BD[i][3]:^12}|{sod_BD[i][4]:^100}|
              {sod_BD[i][5]:^12}|{sod_BD[i][6]:^110}|{sod_BD[i][7]:^40}|{sod_BD[i][8]:^20}|
              {sod_BD[i][9]:^30}|{sod_BD[i][10]:^30}|{sod_BD[i][11]:^40}|{sod_BD[i][12]:^17}|
              {sod_BD[i][13]:^20}|{sod_BD[i][14]:^15}|{sod_BD[i][15]:^40}|{sod_BD[i][16]:^7}|
              {sod_BD[i][17]:^5}|""")

def Vuzstat():
    """Вывод таблицы Vuzstat"""
    con = sq.connect('VUZ.sqlite')
    cur = con.cursor()
    sql = 'SELECT * FROM vuzstat'
    cur.execute(sql)
    polya_BD = cur.description
    sod_BD = cur.execute(sql).fetchall()
    cur.close()
    con.close()
    print(' ',end='')
    print('_'*175)
    print("""|{:^10}|{:^10}|{:^10}|{:^10}|{:^10}|{:^10}|{:^10}|{:^10}|{:^10}|{:^10}|{:^10}|{:^10}|{:^10}|{:^10}|{:^10}|{:^10}|""".format(polya_BD[0][0], polya_BD[1][0],polya_BD[2][0], polya_BD[3][0], polya_BD[4][0], polya_BD[5][0], polya_BD[6][0],polya_BD[7][0], polya_BD[8][0], polya_BD[9][0], polya_BD[10][0], polya_BD[11][0],polya_BD[12][0], polya_BD[13][0], polya_BD[14][0], polya_BD[15][0]))
    for i in range(len(sod_BD)):
        print(f"""|{remove_gaps(sod_BD[i][0]):^10}|{sod_BD[i][1]:^10}|{sod_BD[i][2]:^10}|{sod_BD[i][3]:^10}|{sod_BD[i][4]:^10}|{sod_BD[i][5]:^10}|{sod_BD[i][6]:^10}|{sod_BD[i][7]:^10}|{sod_BD[i][8]:^10}|{sod_BD[i][9]:^10}|{sod_BD[i][10]:^10}|{sod_BD[i][11]:^10}|{sod_BD[i][12]:^10}|{sod_BD[i][13]:^10}|{sod_BD[i][14]:^10}|{sod_BD[i][15]:^10}|""")
    print(' ',end='')
    print('_'*175)

 
while True:
    bd = ''
    while (os.path.isfile(bd)!=True):
        bd = 'VUZ.sqlite'
        if(os.path.isfile(bd)==True): break
        print('Нет такого файла!')
    
    try:
        actions = int(input("""
            Выберите действие:
            1 - отобразить на экране перечень полных наименований ву-
            зов, расположенных в выбранном далее округе и для которых имеется
            информация о сайте вуза
            2 - представить в виде таблицы распределение количества студентов,
            обучающихся в вузах выбранного далее города, по уровням подготовки
            (бакалавр, специалист, магистр)
            3 - отобразить таблицу vuzkart
            4 - отобразить таблицу vuzstat
            5 - завершение сеанса
            """))
    except Error:
        print('Неверный символ')
        continue
    if(actions == 1):
        vuz_name()
    elif (actions == 2):
        students()
    elif (actions == 3):
        Vuzkart()
        """with sq.connect('VUZ.sqlite') as con:
            df = pd.read_sql('SELECT * FROM vuzkart',con)
            print(df)"""
    elif (actions == 4):
        Vuzstat()
    elif (actions == 5):
        break;
    else:
        print('Введено неверное число!')
        
