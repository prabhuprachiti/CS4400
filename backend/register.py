from flask import request
import pymysql
from backend.dbconn import make_conn


def register():
    if request.method == 'POST':
        conn = make_conn()

        try:
            with conn.cursor() as cursor:
                sql = 'INSERT INTO `user_base` (`username`, `email`, `pwd`, `type`)  VALUES (%s, %s, X%s, %s)'
                try:
                    if request.form['type'] == 'admin':
                        return 'error: type'

                    sql_args = (request.form['username'],
                                request.form['email'],
                                request.form['passhash'],
                                request.form['type'])


                    print(sql)
                    print(sql.replace('%s', "'%s'") % sql_args)  # DEBUG

                    cursor.execute(sql, sql_args)

                    table_name = request.form['type']

                    if table_name == 'staff' or table_name == 'visitor':  # DEBUG
                        cursor.execute('INSERT INTO `' + table_name + '` (`username`)  VALUES (%s)',
                                       (request.form['username'],))
                    else:
                        return 'error: table'

                    conn.commit()
                except pymysql.IntegrityError or KeyError as e:
                    return str(e)

                return 'success'
        finally:
            conn.close()
    return "error"
