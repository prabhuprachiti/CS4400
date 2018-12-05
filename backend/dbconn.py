import pymysql.cursors


def make_conn():
    return pymysql.connect(host='academic-mysql.cc.gatech.edu',
                           user='cs4400_group88',
                           password='HZ2cw8zQ',
                           db='cs4400_group88',
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
