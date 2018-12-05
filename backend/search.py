from flask import session, request
import pymysql
from backend.dbconn import make_conn
import csv

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


visit_tables = [
    'exhibit_visit',
    'show_visit'
]


tables_cols = {
    'exhibit': ['name', 'haswater', 'exhsize'],
    'exhibit_show': ['name', 'showtime', 'exhname', 'hostname'],
    'animal': ['name', 'species', 'type', 'age', 'exhname'],
    'note': ['subjname', 'subjspecies', 'notetext'],
    'show_visit': ['name', 'time'],
    'exhibit_visit': ['name', 'time'],
    'user_base': ['username', 'email'],
}

tables_additional_cols = {
    'exhibit': ['numanimals'],
    'exhibit_show': [],
    'animal': [],
    'note': ['authuname', 'notetime'],
    'show_visit': ['exhname'],
    'exhibit_visit': ['numvisits'],
}


def day_match(attr_name, sql_conds, sql_args):
    if request.args.get(attr_name + 'Year') \
            and request.args.get(attr_name + 'Month') \
            and request.args.get(attr_name + 'Day'):
        try:
            checkYear = int(request.args[attr_name + 'Year'])
            checkMonth = int(request.args[attr_name + 'Month'])
            checkDay = int(request.args[attr_name + 'Day'])
        except ValueError:
            return False

        if not (checkYear > 0 and 0 <= checkMonth <= 12 and 0 <= checkDay <= 32):
            return False

        sql_conds.append(attr_name + " >= %s AND " + attr_name + " < %s")
        sql_args.extend(['%s-%s-%s 00:00:00' % (str(checkYear), str(checkMonth), str(checkDay)),
                         '%s-%s-%s 00:00:00' % (str(checkYear), str(checkMonth), str(checkDay + 1))])

    return True


def like_match(attr_name, sql_conds, sql_args):
    if request.args.get(attr_name):
        sql_conds.append(attr_name + ' COLLATE UTF8_GENERAL_CI LIKE %s')
        sql_args.append('%%' + request.args[attr_name] + '%%')


def exact_match(attr_name, sql_conds, sql_args, to_lower=False):
    if request.args.get(attr_name):
        sql_conds.append(attr_name + ' = %s')
        sql_args.append(request.args[attr_name].lower() if to_lower else request.args[attr_name])


def between_match(attr_name, sql_conds, sql_args):
    if request.args.get(attr_name + 'Lo') and request.args.get(attr_name + 'Hi'):
        try:
            numCheckLo = str(int(request.args[attr_name + 'Lo']))
            numCheckHi = str(int(request.args[attr_name + 'Hi']))
        except ValueError:
            return False

        sql_conds.append(attr_name + ' BETWEEN %s AND %s')
        sql_args.extend([numCheckLo, numCheckHi])

    return True


def search():
    if request.method == 'GET' or request.method == 'POST':
        if not session.get('logged_in') or not session['logged_in']:
            return "error: login"

        conn = make_conn()

        try:
            with conn.cursor() as cursor:
                try:
                    target_table = request.args['target'].lower()

                    additional_cols = ''
                    order_by = ''

                    sql_conds = []
                    sql_args = []

                    sql_having_conds = []
                    sql_having_args = []

                    if target_table == 'animal':  # no specific auth required
                        like_match('species', sql_conds, sql_args)
                        exact_match('type', sql_conds, sql_args, to_lower=True)
                        like_match('exhname', sql_conds, sql_args)
                        between_match('age', sql_conds, sql_args)
                        like_match('name', sql_conds, sql_args)
                        order_by = 'name'  # lexicographic order

                    elif target_table == 'exhibit_show' and session['usertype'] != 'staff':  # non-staff authorization
                        like_match('exhname', sql_conds, sql_args)
                        if not day_match('showtime', sql_conds, sql_args):
                            return 'error: date'
                        like_match('name', sql_conds, sql_args)
                        order_by = 'showtime DESC'

                    else:  # specific auth required
                        if session['usertype'] == 'visitor':
                            if target_table in visit_tables:  # a user can only search his own visits!
                                sql_conds.append('visitoruname = %s')
                                sql_args.append(session['username'])

                                order_by = 'time DESC'

                                if not day_match('time', sql_conds, sql_args):
                                    return 'error: date'
                                like_match('name', sql_conds, sql_args)  # show or exh

                                if target_table == 'show_visit':
                                    additional_cols = '(SELECT exhname FROM exhibit_show b WHERE ' \
                                                      'a.name = b.name AND ' \
                                                      'a.time = b.showtime) AS exhname '
                                    like_match('exhname', sql_having_conds, sql_having_args)

                                elif target_table == 'exhibit_visit':
                                    target_table = 'exhibit_visit'
                                    additional_cols = '(SELECT COUNT(*) FROM exhibit_visit b WHERE ' \
                                                      'a.name = b.name AND ' \
                                                      'a.visitoruname = b.visitoruname) AS numvisits '
                                    if request.args.get('numvisitsLo') and request.args.get('numvisitsHi'):
                                        if not between_match('numvisits', sql_having_conds, sql_having_args):
                                            return 'error: numvisits'

                            elif target_table == 'exhibit':
                                additional_cols = '(SELECT COUNT(*) FROM animal b WHERE a.name = b.exhname) ' \
                                                  'AS numanimals '
                                if request.args.get('numanimalsLo') and request.args.get('numanimalsHi'):
                                    if not between_match('numanimals', sql_having_conds, sql_having_args):
                                        return 'error: numanimals'
                                if request.args.get('haswater'):
                                    sql_conds.append('haswater = TRUE' if request.args['haswater']
                                                     else 'haswater = FALSE')
                                if not between_match('exhsize', sql_conds, sql_args):
                                    return 'error: exhsize'
                                exact_match('name', sql_conds, sql_args)
                                order_by = 'name'  # lexicographic order

                            else:
                                return 'error: table'

                        elif session['usertype'] == 'staff':
                            if target_table == 'note':
                                exact_match('subjname', sql_conds, sql_args)
                                exact_match('subjspecies', sql_conds, sql_args)
                                order_by = 'notetime DESC'
                            elif target_table == 'exhibit_show':
                                sql_conds.append('hostname = %s')
                                sql_args.append(session['username'])
                                order_by = 'showtime DESC'
                            elif target_table == 'exhibit':
                                order_by = 'name'  # lexicographic order
                            else:
                                return 'error: table'

                        elif session['usertype'] == 'admin':
                            if target_table == 'visitor' or target_table == 'staff' or target_table == 'user_base':
                                like_match('username', sql_conds, sql_args)
                                like_match('email', sql_conds, sql_args)
                                exact_match('type', sql_conds, sql_args)
                                target_table = 'user_base'

                                order_by = 'username'  # lexicographic order
                            elif target_table == 'exhibit':
                                order_by = 'name'  # lexicographic order
                            else:
                                return 'error: table'

                    if additional_cols == '':
                        sql = ('SELECT * FROM `%s` a WHERE ' % target_table) + ' AND '.join(sql_conds)
                    else:
                        sql = ('SELECT *, %s FROM `%s` a WHERE ' % (additional_cols, target_table)) \
                              + ' AND '.join(sql_conds)

                    if len(sql_conds) == 0:
                        sql += '1'  # select all

                    if len(sql_having_args):
                        sql += ' HAVING ' + ' AND '.join(sql_having_conds)
                        sql_args.extend(sql_having_args)

                    if request.args.get('ordby'):
                        ordby_col = request.args['ordby']

                        if ordby_col not in tables_cols[target_table.split(' ')[0]] and \
                                ordby_col not in tables_additional_cols[target_table.split(' ')[0]]:
                            return 'error: bad_ordby'

                        order_by = ordby_col

                        if request.args.get('ordbydesc') and request.args['ordbydesc'].lower() == 'true':
                            order_by += ' DESC'

                    if order_by != '':
                        sql += ' ORDER BY ' + order_by

                    print(sql)
                    if len(sql_args) > 0:
                        print(sql.replace('%s', "'%s'") % (tuple(sql_args)))  # DEBUG

                    cursor.execute(sql, tuple(sql_args))
                    result = cursor.fetchall()

                    output = StringIO()
                    c = csv.DictWriter(output, [i[0] for i in cursor.description])
                    c.writeheader()
                    for row in result:
                        print(row)
                        c.writerow(row)
                    output.flush()
                    return output.getvalue()

                except pymysql.IntegrityError or KeyError as e:
                    return 'error: ' + str(e)
                except Exception as e:  # DEBUG
                    return 'error: ' + str(e)
        finally:
            conn.close()

    return 'error: http'
