from flask import request, session
import pymysql
from backend.dbconn import make_conn
from backend.search import exact_match


deletable_data_tables = ['staff', 'visitor', 'user_base', 'animal', 'exhibit_show']


def remove_data():
    if request.method == 'GET' or request.method == 'POST':
        if not session.get('logged_in') or not session['logged_in']:
            return "error"

        conn = make_conn()

        try:
            with conn.cursor() as cursor:
                try:
                    target_table = request.args['target'].lower()

                    if session['usertype'] != 'admin':
                        return 'error: auth'

                    if target_table not in deletable_data_tables:
                        return 'error: table'

                    sql_conds = []
                    sql_args = []

                    if target_table == 'staff' or target_table == 'visitor' or target_table == 'user_base':
                        target_table = 'user_base'
                        exact_match('username', sql_conds, sql_args)

                    elif target_table == 'animal' and request.args.get('name') and request.args.get('species'):
                        exact_match('name', sql_conds, sql_args)
                        exact_match('species', sql_conds, sql_args)

                    elif target_table == 'exhibit_show' and request.args.get('name') and request.args.get('showtime'):
                        exact_match('name', sql_conds, sql_args)
                        exact_match('showtime', sql_conds, sql_args)

                    else:
                        return 'error: table'

                    sql = ('DELETE FROM `%s` WHERE ' % target_table) + ' AND '.join(sql_conds)

                    print(sql)
                    if len(sql_args) > 0:
                        print(sql.replace('%s', "'%s'") % (tuple(sql_args)))  # DEBUG

                    cursor.execute(sql, tuple(sql_args))

                    conn.commit()

                    return 'success'
                except pymysql.IntegrityError or KeyError as e:
                    return 'error: ' + str(e)
                except Exception as e:  # DEBUG
                    return 'error: ' + str(e)
        finally:
            conn.close()

    return 'error: http'
