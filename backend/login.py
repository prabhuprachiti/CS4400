from flask import session, request
import pymysql
from backend.dbconn import make_conn


def login():
    if request.method == 'POST':
        conn = make_conn()

        try:
            with conn.cursor() as cursor:
                sql = "SELECT `username`, `email`, `pwd`, `type` FROM `user_base` WHERE `email` = %s OR `username` = %s"

                try:
                    sql_args = (request.form['username'], request.form['username'],)

                    print(sql)
                    print(sql.replace('%s', "'%s'") % sql_args)  # DEBUG

                    cursor.execute(sql, sql_args)
                    result = cursor.fetchall()
                    if len(result) != 1:
                        return "error: not_found"

                    if request.form['passhash'] != result[0]['pwd'].hex():
                        # print(sha256(request.form['password'].encode('utf-8')).hexdigest(), result[0]['pwd'].hex())
                        return "pass"

                    session['username'] = result[0]['username']
                    session['usertype'] = result[0]['type']
                    session['logged_in'] = True

                except pymysql.IntegrityError or KeyError as e:
                    return str(e)

                return session['usertype']
        finally:
            conn.close()
    return "error"
