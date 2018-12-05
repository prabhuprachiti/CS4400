from flask import request, session
import pymysql
from backend.dbconn import make_conn


tables_cols_users = {
    'exhibit': (['name', 'haswater', 'exhsize'], ['admin']),  # DEBUG
    'exhibit_show': (['name', 'showtime', 'exhname', 'hostname'], ['admin']),
    'animal': (['name', 'species', 'type', 'age', 'exhname'], ['admin']),
    'note': (['subjname', 'subjspecies', 'notetext'], ['staff']),
    'show_visit': (['name', 'time'], ['visitor']),
    'exhibit_visit': (['name', 'time'], ['visitor']),
}


def add_data():
    if request.method == 'GET' or request.method == 'POST':
        if not session.get('logged_in') or not session['logged_in']:
            return "error"

        conn = make_conn()

        try:
            with conn.cursor() as cursor:
                try:
                    target_table = request.args['target'].lower()

                    if target_table not in tables_cols_users or \
                            session['usertype'] not in tables_cols_users[target_table][1]:
                        return 'error: table'

                    cols = tables_cols_users[target_table][0].copy()

                    sql_args = []

                    if target_table == 'note':
                        cols.insert(0, 'authuname')
                        sql_args = [session['username']]
                    elif target_table == 'show_visit' or target_table == 'exhibit_visit':
                        cols.insert(0, 'visitoruname')
                        sql_args = [session['username']]

                    sql = 'INSERT INTO ' + target_table + '(' + ','.join(cols) + ') VALUES (' + ','.join((['%s'] * len(cols))) + ')'

                    for col in tables_cols_users[target_table][0]:  # list of args
                        if request.form.get(col):
                            sql_args.append(request.form[col])
                        else:
                            return 'error: missing_val'

                    print(sql)
                    if len(sql_args) > 0:
                        print(sql.replace('%s', "'%s'") % (tuple(sql_args)))  # DEBUG

                    cursor.execute(sql, tuple(sql_args))

                    conn.commit()

                    return 'success'
                except pymysql.IntegrityError or KeyError as e:
                    return str(e)
                except Exception as e:  # DEBUG
                    return str(e)
        finally:
            conn.close()

    return 'error: http'
