import sys
import requests
from email.utils import parseaddr
from hashlib import sha256
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from UI.loginform import Ui_MainWindow as lf
from UI.visitorfunctionality import Ui_MainWindow as vf
from UI.searchexhibit import Ui_MainWindow as search_exhibit
from UI.searchshows import Ui_MainWindow as search_shows
from UI.searchanimals import Ui_MainWindow as search_animals
from UI.exhibithistory import Ui_MainWindow as exhibit_history
from UI.showhistory import Ui_MainWindow as show_history
from UI.exhibitdetail import Ui_MainWindow as exhibit_detail
from UI.animaldetail import Ui_MainWindow as animal_detail
from UI.stafffunctionality import Ui_MainWindow as sf
from UI.staffsearchanimals import Ui_MainWindow as staff_search_animals
from UI.animalcare import Ui_MainWindow as animal_care
from UI.staffshowhistory import Ui_MainWindow as staff_show_history
from UI.adminfunctionality import Ui_MainWindow as af
from UI.viewvisitors import Ui_MainWindow as view_v
from UI.viewstaff import Ui_MainWindow as view_s
from UI.addanimals import Ui_MainWindow as add_animal
from UI.adminviewshows import Ui_MainWindow as admin_view_shows
from UI.adminviewanimals import Ui_MainWindow as admin_view_animals
from UI.addshows import Ui_MainWindow as add_show
from UI.registration import Ui_MainWindow as reg
import csv
import re
import datetime

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

server_addr = 'http://127.0.0.1:5000/backend/'


class Object(object):
    pass


last_request = Object()
last_request.cookies = {}  # PLACEHOLDER!


current_session_cookies = {}


# These values determine which cols of the response data go to output and in what order
col_order = {
    'animal': ['name', 'species', 'exhname', 'age', 'type'],
    'exhibit_show': ['name', 'exhname', 'showtime'],
    'exhibit': ['name', 'exhsize', 'numanimals', 'haswater'],
    'exhibit_visit': ['name', 'time', 'numvisits'],
    'show_visit': ['name', 'time', 'exhname'],
    'note': ['authuname', 'notetext', 'notetime'],
    'user_base': ['username', 'email']
}


def make_req(endpoint, getargs={}, postargs={}):
    global last_request
    global current_session_cookies
    last_request = requests.post(server_addr + endpoint,
                                 params=getargs,
                                 data=postargs,
                                 cookies=current_session_cookies)
    if len(last_request.cookies) > 0:
        current_session_cookies = last_request.cookies

    return last_request


def logout():
    global last_request
    global current_session_cookies
    res = make_req('logout')
    if res.text != 'success':
        error_msgbox('Cannot log out!')
    last_request = Object()
    last_request.cookies = {}
    current_session_cookies = {}


def msgbox(msgtext):
    dialog = QtWidgets.QMessageBox()
    dialog.setText(msgtext)
    dialog.exec_()


def error_msgbox(msgtext):
    error_dialog = QtWidgets.QErrorMessage()
    error_dialog.showMessage(msgtext)
    error_dialog.exec_()


class MyTableWidgetItem(QtWidgets.QTableWidgetItem):
    def __init__(self, text):
        QtWidgets.QTableWidgetItem.__init__(self, text, QtWidgets.QTableWidgetItem.UserType)

    def __lt__(self, other):
        return False


def insert_into_qtablewidget(table, colorder, data, num_cols=-1):
    global col_order
    rowPosition = table.rowCount()
    table.insertRow(rowPosition)

    i = 0
    for key in (col_order[colorder] if num_cols <= 0 else col_order[colorder][:num_cols]):
        table.setItem(rowPosition, i, MyTableWidgetItem(data[key]))
        i += 1


def load_search_results(table_widget, table_name, ordby_col, ordby_desc, data_args={}, num_cols=-1):
    table_widget.setRowCount(0)
    args_vals = data_args.copy()
    args_vals['target'] = table_name

    if ordby_desc is not None and ordby_col is not None:
        args_vals['ordby'] = ordby_col
        args_vals['ordbydesc'] = ordby_desc

    res = make_req('search', getargs=args_vals)

    if res.text.split(':')[0] == 'error':
        error_msgbox(res.text)
        return []

    csvdata = StringIO(res.text)
    reader = csv.DictReader(csvdata)
    rows = []
    for row in reader:
        insert_into_qtablewidget(table_widget, table_name, row, num_cols)
        rows.append(row)
    return rows


def populate_combobox(combobox_widget, table_name, col_name, default_empty=True, data_args={}):
    combobox_widget.clear()
    args_vals = data_args.copy()
    args_vals['target'] = table_name
    res = make_req('search', getargs=args_vals)

    if res.text.split(':')[0] == 'error':
        error_msgbox(res.text)

    csvdata = StringIO(res.text)
    reader = csv.DictReader(csvdata)
    rows = [''] if default_empty else []
    for row in reader:
        rows.append(row[col_name])

    combobox_widget.addItems(rows)

def center(window):
    qr = window.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    window.move(qr.topLeft())


class LoginForm(QMainWindow):  # open the login form. This is the main window
    def __init__(self):
        super(LoginForm, self).__init__()
        self.ui = lf()
        self.ui.setupUi(self)
        center(self)
        self.show()
        self.ui.pushButton.clicked.connect(self.performLogin)
        self.ui.pushButton_2.clicked.connect(self.openRegistration)

    # check if logging in as staff or visitor or admin and call the appropriate function
    def performLogin(self):
        if self.ui.lineEdit.text() == '' or self.ui.lineEdit_2.text() == '':
            error_msgbox('All fields must be filled!')
            return

        res = make_req('login', postargs={'username': self.ui.lineEdit.text(),
                                          'passhash': sha256(self.ui.lineEdit_2.text().encode('utf-8')).hexdigest()})

        if res.text == 'visitor':
            self.openVisitorFunctionality()
        elif res.text == 'staff':
            self.openStaffFunctionality()
        elif res.text == 'admin':
            self.openAdminFunctionality()
        elif res.text == 'pass':
            error_msgbox('Wrong Password!')
        else:
            error_msgbox(res.text)

    def openVisitorFunctionality(self):  # logging in as visitors
        self.close()
        self.Open = VisitorFunctionality()

    def openStaffFunctionality(self):  # logging in as staff
        self.close()
        self.Open = StaffFunctionality()

    def openAdminFunctionality(self):  # logging in as admin
        self.close()
        self.Open = AdminFunctionality()

    def openRegistration(self):  # registering as a new user
        self.close()
        self.Open = Registration()

class VisitorFunctionality(QMainWindow):  # visitor functionality
    # search exhibits (exhibit detail), search shows (exhibit detail), search animals (animal detail),
    # exhibit history (exhibit detail, animal detail), show history and logout

    def __init__(self):
        super(VisitorFunctionality, self).__init__()
        self.ui = vf()
        self.ui.setupUi(self)
        center(self)
        self.show()

        self.ui.pushButton.clicked.connect(self.openSearchExhibits)
        self.ui.pushButton_2.clicked.connect(self.openSearchShows)
        self.ui.pushButton_3.clicked.connect(self.openSearchAnimals)
        self.ui.pushButton_4.clicked.connect(self.openExhibitHistory)
        self.ui.pushButton_5.clicked.connect(self.openShowHistory)
        self.ui.pushButton_6.clicked.connect(self.openLogout)

    def openSearchExhibits(self):  # visitor search exhibit
        self.close()
        self.Open = SearchExhibits()

    def openSearchShows(self):  # visitor search show
        self.close()
        self.Open = SearchShows()

    def openSearchAnimals(self):  # visitor search animals
        self.close()
        self.Open = SearchAnimals()

    def openExhibitHistory(self):  # visitor exhibit history
        self.close()
        self.Open = ExhibitHistory()

    def openShowHistory(self):  # visitor show history
        self.close()
        self.Open = ShowHistory()

    def openLogout(self):  # logout -- go back to login page
        logout()
        self.close()
        self.Open = LoginForm()


class SearchExhibits(QMainWindow):  # visitor search exhibits

    def __init__(self):
        super(SearchExhibits, self).__init__()
        self.ui = search_exhibit()
        self.ui.setupUi(self)
        center(self)
        self.show()
        self.ui.tableWidget.clicked.connect(self.openExhibitDetail)
        self.ui.pushButton.clicked.connect(self.searchExhibits)
        self.rows = load_search_results(self.ui.tableWidget, 'exhibit', None, None)

        self.ordby_key = None
        self.ordby_desc = None
        self.ui.tableWidget.horizontalHeader().sortIndicatorChanged.connect(self.switchSort)

        self.ui.pushButton_2.clicked.connect(self.goBack)

    def goBack(self):
        self.close()
        self.Open = VisitorFunctionality()

    def switchSort(self, col_index, ord):
        self.ordby_key = col_order['exhibit'][col_index]
        self.ordby_desc = (ord != QtCore.Qt.DescendingOrder)
        self.ui.tableWidget.setSortingEnabled(False)
        self.searchExhibits()
        self.ui.tableWidget.setSortingEnabled(True)

    def openExhibitDetail(self, item):  # opening the exhibit detail page when clicked on an exhibit
        self.close()
        self.Open = ExhibitDetail(self.rows[item.row()]['name'])

    def searchExhibits(self):
        getdata = {}
        if self.ui.lineEdit.text() != '':
            getdata['name'] = self.ui.lineEdit.text()
        if self.ui.spinBox_2.value() != 0 and self.ui.spinBox.value() <= self.ui.spinBox_2.value():
            getdata['numanimalsLo'] = self.ui.spinBox.value()
            getdata['numanimalsHi'] = self.ui.spinBox_2.value()
        if self.ui.spinBox_4.value() != 0 and self.ui.spinBox_3.value() <= self.ui.spinBox_4.value():
            getdata['exhsizeLo'] = self.ui.spinBox_3.value()
            getdata['exhsizeHi'] = self.ui.spinBox_4.value()
        if self.ui.comboBox.currentText() != '':
            getdata['haswater'] = '1' if self.ui.comboBox.currentText() == 'Yes' else '0'
        self.rows = load_search_results(self.ui.tableWidget, 'exhibit', self.ordby_key, self.ordby_desc, getdata)


class SearchShows(QMainWindow):  # visitor search shows
    def __init__(self):
        super(SearchShows, self).__init__()
        self.ui = search_shows()
        self.ui.setupUi(self)
        center(self)
        self.show()
        self.ui.pushButton.clicked.connect(self.searchShows)
        self.ui.pushButton_2.clicked.connect(self.logShowVisit)
        self.ui.tableWidget.clicked.connect(self.openExhibitDetail)
        self.rows = load_search_results(self.ui.tableWidget, 'exhibit_show', None, None)
        populate_combobox(self.ui.comboBox_2, 'exhibit', 'name')

        self.ordby_key = None
        self.ordby_desc = None
        self.ui.tableWidget.horizontalHeader().sortIndicatorChanged.connect(self.switchSort)

        self.ui.pushButton_3.clicked.connect(self.goBack)

    def goBack(self):
        self.close()
        self.Open = VisitorFunctionality()


    def switchSort(self, col_index, ord):
        self.ordby_key = col_order['exhibit_show'][col_index]
        self.ordby_desc = (ord != QtCore.Qt.DescendingOrder)
        self.ui.tableWidget.setSortingEnabled(False)
        self.searchShows()
        self.ui.tableWidget.setSortingEnabled(True)

    def searchShows(self):
        showdate = self.ui.dateEdit.date().toPyDate()

        getdata = {}
        if self.ui.checkBox.isChecked():
            getdata['showtimeDay'] = str(showdate.day)
            getdata['showtimeMonth'] = str(showdate.month)
            getdata['showtimeYear'] = str(showdate.year)
        if self.ui.lineEdit.text() != '':
            getdata['name'] = self.ui.lineEdit.text()
        if self.ui.comboBox_2.currentText() != '':
            getdata['exhname'] = self.ui.comboBox_2.currentText()
        self.rows = load_search_results(self.ui.tableWidget, 'exhibit_show', self.ordby_key, self.ordby_desc, getdata)

    def logShowVisit(self):
        rows = sorted(set(index.row() for index in self.ui.tableWidget.selectedIndexes()))
        for row in rows:
            res = make_req('add_data',
                           getargs={'target': 'show_visit'},
                           postargs={'name': self.rows[row]['name'],
                                     'time': self.rows[row]['showtime']})

            make_req('add_data',
                    getargs={'target': 'exhibit_visit'},
                    postargs={'name': self.rows[row]['exhname'],
                            'time': self.rows[row]['showtime']})

            if res.text != 'success':
                error_msgbox(res.text)
            else:
                msgbox('Logged visit!')

    def openExhibitDetail(self, item):  # opening the exhibit detail page when clicked on an exhibit
        if item.column() == 1:
            self.close()
            self.Open = ExhibitDetail(self.rows[item.row()]['exhname'])


class SearchAnimals(QMainWindow):  # visitor search animals
    def __init__(self):
        super(SearchAnimals, self).__init__()
        self.ui = search_animals()
        self.ui.setupUi(self)
        center(self)
        self.show()
        self.ui.tableWidget.clicked.connect(self.openAnimalDetail)
        self.ui.pushButton.clicked.connect(self.searchAnimals)
        self.rows = load_search_results(self.ui.tableWidget, 'animal', None, None)
        populate_combobox(self.ui.comboBox_2, 'exhibit', 'name')

        self.ordby_key = None
        self.ordby_desc = None
        self.ui.tableWidget.horizontalHeader().sortIndicatorChanged.connect(self.switchSort)

        self.ui.pushButton_2.clicked.connect(self.goBack)

    def goBack(self):
        self.close()
        self.Open = VisitorFunctionality()

    def switchSort(self, col_index, ord):
        self.ordby_key = col_order['animal'][col_index]
        self.ordby_desc = (ord != QtCore.Qt.DescendingOrder)
        self.ui.tableWidget.setSortingEnabled(False)
        self.searchAnimals()
        self.ui.tableWidget.setSortingEnabled(True)

    def searchAnimals(self):
        getdata = {}
        if self.ui.lineEdit.text() != '':
            getdata['name'] = self.ui.lineEdit.text()
        if self.ui.lineEdit_2.text() != '':
            getdata['species'] = self.ui.lineEdit_2.text()
        if self.ui.comboBox_2.currentText() != '':
            getdata['exhname'] = self.ui.comboBox_2.currentText()
        if self.ui.spinBox_2.value() != 0 and self.ui.spinBox.value() <= self.ui.spinBox_2.value():
            getdata['ageLo'] = self.ui.spinBox.value()
            getdata['ageHi'] = self.ui.spinBox_2.value()
        if self.ui.comboBox.currentText() != '':
            getdata['type'] = self.ui.comboBox.currentText()
        self.rows = load_search_results(self.ui.tableWidget, 'animal', self.ordby_key, self.ordby_desc, getdata)

    def openAnimalDetail(self, item):  # opening the animal care page when clicked on an animal
        self.close()
        if item.column() == 2:  # exhibit
            self.Open = ExhibitDetail(self.rows[item.row()]['exhname'])
        else:
            self.Open = AnimalDetail(self.rows[item.row()])


class ExhibitHistory(QMainWindow):  # visitor exhibit history
    def __init__(self):
        super(ExhibitHistory, self).__init__()
        self.ui = exhibit_history()
        self.ui.setupUi(self)
        center(self)
        self.show()
        self.ui.tableWidget.clicked.connect(self.openExhibitDetail)
        self.ui.pushButton.clicked.connect(self.searchExhibits)
        self.rows = load_search_results(self.ui.tableWidget, 'exhibit_visit', None, None)

        self.ordby_key = None
        self.ordby_desc = None
        self.ui.tableWidget.horizontalHeader().sortIndicatorChanged.connect(self.switchSort)

        self.ui.pushButton_2.clicked.connect(self.goBack)

    def goBack(self):
        self.close()
        self.Open = VisitorFunctionality()

    def switchSort(self, col_index, ord):
        self.ordby_key = col_order['exhibit_visit'][col_index]
        self.ordby_desc = (ord != QtCore.Qt.DescendingOrder)
        self.ui.tableWidget.setSortingEnabled(False)
        self.searchExhibits()
        self.ui.tableWidget.setSortingEnabled(True)

    def openExhibitDetail(self, item):  # opening the exhibit detail page when clicked on an exhibit
        self.close()
        self.Open = ExhibitDetail(self.rows[item.row()]['name'])

    def searchExhibits(self):
        getdata = {}
        timedate = self.ui.dateEdit.date().toPyDate()
        if self.ui.checkBox.isChecked():
            getdata['timeDay'] = str(timedate.day)
            getdata['timeMonth'] = str(timedate.month)
            getdata['timeYear'] = str(timedate.year)
        if self.ui.lineEdit.text() != '':
            getdata['name'] = self.ui.lineEdit.text()
        if self.ui.spinBox_2.value() != 0 and self.ui.spinBox.value() <= self.ui.spinBox_2.value():
            getdata['numvisitsLo'] = self.ui.spinBox.value()
            getdata['numvisitsHi'] = self.ui.spinBox_2.value()
        self.rows = load_search_results(self.ui.tableWidget, 'exhibit_visit', self.ordby_key, self.ordby_desc, getdata)


class ShowHistory(QMainWindow):  # visitor show history
    def __init__(self):
        super(ShowHistory, self).__init__()
        self.ui = show_history()
        self.ui.setupUi(self)
        center(self)
        self.show()
        self.ui.tableWidget.clicked.connect(self.openExhibitDetail)
        self.ui.pushButton.clicked.connect(self.searchShows)
        self.rows = load_search_results(self.ui.tableWidget, 'show_visit', None, None)
        populate_combobox(self.ui.comboBox_2, 'exhibit', 'name')

        self.ordby_key = None
        self.ordby_desc = None
        self.ui.tableWidget.horizontalHeader().sortIndicatorChanged.connect(self.switchSort)

        self.ui.pushButton_2.clicked.connect(self.goBack)

    def goBack(self):
        self.close()
        self.Open = VisitorFunctionality()

    def switchSort(self, col_index, ord):
        self.ordby_key = col_order['show_visit'][col_index]
        self.ordby_desc = (ord != QtCore.Qt.DescendingOrder)
        self.ui.tableWidget.setSortingEnabled(False)
        self.searchShows()
        self.ui.tableWidget.setSortingEnabled(True)

    def openExhibitDetail(self, item):  # opening the exhibit detail page when clicked on an exhibit
        self.close()
        self.Open = ExhibitDetail(self.rows[item.row()]['exhname'])

    def searchShows(self):
        getdata = {}
        timedate = self.ui.dateEdit.date().toPyDate()
        if self.ui.checkBox.isChecked():
            getdata['timeDay'] = str(timedate.day)
            getdata['timeMonth'] = str(timedate.month)
            getdata['timeYear'] = str(timedate.year)
        if self.ui.lineEdit.text() != '':
            getdata['name'] = self.ui.lineEdit.text()
        if self.ui.comboBox_2.currentText() != '':
            getdata['exhname'] = self.ui.comboBox_2.currentText()

        self.rows = load_search_results(self.ui.tableWidget, 'show_visit', self.ordby_key, self.ordby_desc, getdata)


class ExhibitDetail(QMainWindow):  # exhibit detail
    def __init__(self, exhname):
        super(ExhibitDetail, self).__init__()
        self.exhname = exhname
        self.ui = exhibit_detail()
        self.ui.setupUi(self)
        center(self)
        self.show()

        self.ui.name.setText('Name: ' + exhname)

        res = make_req('search', getargs={'target': 'exhibit',
                                          'name': exhname})

        if res.text.split(':')[0] == 'error':
            error_msgbox(res.text)
            return

        csvdata = StringIO(res.text)
        reader = csv.DictReader(csvdata)
        for row in reader:
            self.ui.size.setText('Size: ' + row['exhsize'])
            self.ui.numanimals.setText('Num Animals: ' + row['numanimals'])
            self.ui.waterfeature.setText('Water Feature: ' + ('Yes' if row['haswater'] == '1' else 'No'))

        self.rows = load_search_results(self.ui.tableWidget, 'animal', None, None, num_cols=2, data_args={'exhname': exhname})
        self.ui.tableWidget.clicked.connect(self.openAnimalDetail)

        self.ui.pushButton.clicked.connect(self.logExhibitVisit)

        self.ordby_key = None
        self.ordby_desc = None
        self.ui.tableWidget.horizontalHeader().sortIndicatorChanged.connect(self.switchSort)

        self.ui.pushButton_2.clicked.connect(self.goBack)

    def goBack(self):
        self.close()
        self.Open = VisitorFunctionality()

    def switchSort(self, col_index, ord):
        self.ordby_key = col_order['animal'][col_index]
        self.ordby_desc = (ord != QtCore.Qt.DescendingOrder)
        self.ui.tableWidget.setSortingEnabled(False)
        self.rows = load_search_results(self.ui.tableWidget, 'animal', self.ordby_key, self.ordby_desc, num_cols=2,
                                        data_args={'exhname': self.exhname})
        self.ui.tableWidget.setSortingEnabled(True)

    def openAnimalDetail(self, item):  # opening the animal detail page when clicked on an animal
        self.close()
        self.Open = AnimalDetail(self.rows[item.row()])

    def logExhibitVisit(self):
        res = make_req('add_data',
                       getargs={'target': 'exhibit_visit'},
                       postargs={'name': self.exhname,
                                 'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        if res.text != 'success':
            error_msgbox(res.text)
            return
        msgbox('Logged visit!')


class AnimalDetail(QMainWindow):  # animal detail
    def __init__(self, data_row):
        super(AnimalDetail, self).__init__()
        self.data_row = data_row
        self.ui = animal_detail()
        self.ui.setupUi(self)
        center(self)
        self.show()

        self.ui.name.setText('Name: ' + data_row['name'])
        self.ui.species.setText('Species: ' + data_row['species'])
        self.ui.age.setText('Age: ' + data_row['age'])
        self.ui.exhibit.setText('Exhibit: ' + data_row['exhname'])
        self.ui.type.setText('Type: ' + data_row['type'])

        self.ui.pushButton.clicked.connect(self.goBack)

    def goBack(self):
        self.close()
        self.Open = VisitorFunctionality()


class Registration(QMainWindow):  # registration page
    def __init__(self):
        super(Registration, self).__init__()
        self.ui = reg()
        self.ui.setupUi(self)
        center(self)
        self.show()
        self.ui.pushButton.clicked.connect(self.registerVisitor)
        self.ui.pushButton_2.clicked.connect(self.registerStaff)

    def register(self, type):
        if self.ui.lineEdit.text() == '' or self.ui.lineEdit_2.text() == '' or self.ui.lineEdit_3.text() == '':
            error_msgbox('All fields must be filled!')
            return

        if '@' not in parseaddr(self.ui.lineEdit.text())[1]:
            error_msgbox("Malformed email!")
            return

        if self.ui.lineEdit_3.text() != self.ui.lineEdit_4.text():
            error_msgbox("Passwords don't match!")
            return

        if len(self.ui.lineEdit_3.text()) < 8:
            error_msgbox("Password roo short, should be at least 8 characters!")
            return

        res = make_req('register', postargs={'email': self.ui.lineEdit.text(),
                                             'username': self.ui.lineEdit_2.text(),
                                             'passhash': sha256(self.ui.lineEdit_3.text().encode('utf-8')).hexdigest(),
                                             'type': type})
        if res.text == 'success':
            self.close()
            self.Open = LoginForm()
        else:
            error_msgbox(res.text)

    def registerVisitor(self):
        self.register('visitor')

    def registerStaff(self):
        self.register('staff')

class StaffFunctionality(QMainWindow):  # staff functionality
    # search animals (animal detail, animal care), search shows, logout
    def __init__(self):
        super(StaffFunctionality, self).__init__()
        self.ui = sf()
        self.ui.setupUi(self)
        center(self)
        self.show()

        self.ui.pushButton.clicked.connect(self.openStaffSearchAnimals)
        self.ui.pushButton_2.clicked.connect(self.openStaffSearchShows)
        self.ui.pushButton_3.clicked.connect(self.openLogout)

    def openStaffSearchAnimals(self):  # staff search animals
        self.close()
        self.Open = StaffSearchAnimals()

    def openStaffSearchShows(self):  # staff search shows
        self.close()
        self.Open = StaffSearchShows()

    def openLogout(self):  # logout -- go back to the login page
        logout()
        self.close()
        self.Open = LoginForm()

class StaffSearchAnimals(QMainWindow):  # staff search animals
    def __init__(self):
        super(StaffSearchAnimals, self).__init__()
        self.ui = staff_search_animals()
        self.ui.setupUi(self)
        center(self)
        self.show()
        self.ui.tableWidget.clicked.connect(self.openAnimalDetail)
        self.ui.pushButton.clicked.connect(self.searchAnimals)
        self.rows = load_search_results(self.ui.tableWidget, 'animal', None, None)

        populate_combobox(self.ui.comboBox_2, 'exhibit', 'name')

        self.ordby_key = None
        self.ordby_desc = None
        self.ui.tableWidget.horizontalHeader().sortIndicatorChanged.connect(self.switchSort)

        self.ui.pushButton_2.clicked.connect(self.goBack)

    def goBack(self):
        self.close()
        self.Open = StaffFunctionality()

    def switchSort(self, col_index, ord):
        self.ordby_key = col_order['animal'][col_index]
        self.ordby_desc = (ord != QtCore.Qt.DescendingOrder)
        self.ui.tableWidget.setSortingEnabled(False)
        self.searchAnimals()
        self.ui.tableWidget.setSortingEnabled(True)

    def searchAnimals(self):
        getdata = {}
        if self.ui.lineEdit.text() != '':
            getdata['name'] = self.ui.lineEdit.text()
        if self.ui.lineEdit_2.text() != '':
            getdata['species'] = self.ui.lineEdit_2.text()
        if self.ui.comboBox_3.currentText() != '':
            getdata['type'] = self.ui.comboBox_3.currentText()
        if self.ui.spinBox_2.value() != 0 and self.ui.spinBox.value() <= self.ui.spinBox_2.value():
            getdata['ageLo'] = self.ui.spinBox.value()
            getdata['ageHi'] = self.ui.spinBox_2.value()
        if self.ui.comboBox_2.currentText() != '':
            getdata['exhname'] = self.ui.comboBox_2.currentText()
        self.rows = load_search_results(self.ui.tableWidget, 'animal', self.ordby_key, self.ordby_desc, getdata)

    def openAnimalDetail(self, item):  # opening the animal care page when clicked on an animal
        self.close()
        self.Open = AnimalCare(self.rows[item.row()])

class AnimalCare(QMainWindow):  # animal care
    def __init__(self, data_row):
        super(AnimalCare, self).__init__()
        self.data_row = data_row
        self.ui = animal_care()
        self.ui.setupUi(self)
        center(self)
        self.show()

        self.ui.name.setText('Name: ' + data_row['name'])
        self.ui.species.setText('Species: ' + data_row['species'])
        self.ui.age.setText('Age: ' + data_row['age'])
        self.ui.exhibit.setText('Exhibit: ' + data_row['exhname'])
        self.ui.type.setText('Type: ' + data_row['type'])

        self.ui.pushButton.clicked.connect(self.addNote)
        load_search_results(self.ui.tableWidget, 'note', None, None, data_args={'subjname': self.data_row['name'],
                                                                                'subjspecies': self.data_row['species']
                                                                                })

        self.ordby_key = None
        self.ordby_desc = None
        self.ui.tableWidget.horizontalHeader().sortIndicatorChanged.connect(self.switchSort)

        self.ui.pushButton_2.clicked.connect(self.goBack)

    def goBack(self):
        self.close()
        self.Open = StaffFunctionality()

    def switchSort(self, col_index, ord):
        self.ordby_key = col_order['note'][col_index]
        self.ordby_desc = (ord != QtCore.Qt.DescendingOrder)
        self.ui.tableWidget.setSortingEnabled(False)
        load_search_results(self.ui.tableWidget, 'note', self.ordby_key, self.ordby_desc,
                            data_args={'subjname': self.data_row['name'],
                                       'subjspecies': self.data_row['species']})
        self.ui.tableWidget.setSortingEnabled(True)

    def addNote(self):
        res = make_req('add_data',
                       getargs={'target': 'note'},
                       postargs={'subjname': self.data_row['name'],
                                 'subjspecies': self.data_row['species'],
                                 'notetext': self.ui.textEdit.toPlainText()})
        if res.text != 'success':
            error_msgbox(res.text)
        self.ui.textEdit.setText('')
        load_search_results(self.ui.tableWidget, 'note', self.ordby_key, self.ordby_desc)


class StaffSearchShows(QMainWindow):  # staff search shows
    def __init__(self):
        super(StaffSearchShows, self).__init__()
        self.ui = staff_show_history()
        self.ui.setupUi(self)
        center(self)
        self.show()
        load_search_results(self.ui.tableWidget, 'exhibit_show', None, None)

        self.ordby_key = None
        self.ordby_desc = None
        self.ui.tableWidget.horizontalHeader().sortIndicatorChanged.connect(self.switchSort)
        self.ui.pushButton.clicked.connect(self.goBack)

    def goBack(self):
        self.close()
        self.Open = StaffFunctionality()

    def switchSort(self, col_index, ord):
        self.ordby_key = col_order['exhibit_show'][col_index]
        self.ordby_desc = (ord != QtCore.Qt.DescendingOrder)
        self.ui.tableWidget.setSortingEnabled(False)
        load_search_results(self.ui.tableWidget, 'exhibit_show', self.ordby_key, self.ordby_desc)
        self.ui.tableWidget.setSortingEnabled(True)


class AdminFunctionality(QMainWindow):  # admin functionality
    # view visitors, view staff, add animals, view shows, view animals, add shows, logout
    def __init__(self):
        super(AdminFunctionality, self).__init__()
        self.ui = af()
        self.ui.setupUi(self)
        center(self)
        self.show()

        self.ui.pushButton.clicked.connect(self.openViewVisitors)
        #self.ui.pushButton.clicked.connect(self.previouswindow)
        self.ui.pushButton_2.clicked.connect(self.openViewStaff)
        self.ui.pushButton_3.clicked.connect(self.openAddAnimal)
        self.ui.pushButton_4.clicked.connect(self.openAdminViewShows)
        self.ui.pushButton_5.clicked.connect(self.openAdminViewAnimals)
        self.ui.pushButton_6.clicked.connect(self.openAddShow)
        self.ui.pushButton_7.clicked.connect(self.openLogOut)

    def openViewVisitors(self):  # view visitors
        self.close()
        self.Open = ViewVisitors()

    def openViewStaff(self):  # view staff
        self.close()
        self.Open = ViewStaff()

    def openAddAnimal(self):  # add animals
        self.close()
        self.Open = AddAnimal()

    def openAdminViewShows(self):  # view shows
        self.close()
        self.Open = AdminViewShows()

    def openAdminViewAnimals(self):  # view animals
        self.close()
        self.Open = AdminViewAnimals()

    def openAddShow(self):  # add shows
        self.close()
        self.Open = AddShow()

    def openLogOut(self):  # logout -- go back to the login page
        logout()
        self.close()
        self.Open = LoginForm()

class ViewVisitors(QMainWindow):  # view/search/delete visitors
    def __init__(self):
        super(ViewVisitors, self).__init__()
        self.ui = view_v()
        self.ui.setupUi(self)
        center(self)
        self.show()
        load_search_results(self.ui.tableWidget, 'user_base', None, None, {'type': 'visitor'})
        self.ui.pushButton.clicked.connect(self.searchVisitor)
        self.ui.pushButton_2.clicked.connect(self.deleteVisitor)

        self.ordby_key = None
        self.ordby_desc = None
        self.ui.tableWidget.horizontalHeader().sortIndicatorChanged.connect(self.switchSort)

        self.ui.pushButton_3.clicked.connect(self.goBack)

    def goBack(self):
        self.close()
        self.Open = AdminFunctionality()

    def switchSort(self, col_index, ord):
        self.ordby_key = col_order['user_base'][col_index]
        self.ordby_desc = (ord != QtCore.Qt.DescendingOrder)
        self.ui.tableWidget.setSortingEnabled(False)
        self.searchVisitor()
        self.ui.tableWidget.setSortingEnabled(True)

    def searchVisitor(self):
        getdata = {'type': 'visitor'}
        if self.ui.lineEdit.text() != '':
            getdata['email'] = self.ui.lineEdit.text()
        if self.ui.lineEdit_2.text() != '':
            getdata['username'] = self.ui.lineEdit_2.text()
        load_search_results(self.ui.tableWidget, 'user_base', self.ordby_key, self.ordby_desc, getdata)

    def deleteVisitor(self):
        rows = sorted(set(index.row() for index in self.ui.tableWidget.selectedIndexes()))
        for row in rows:
            username = self.ui.tableWidget.item(row, 0).text()
            res = make_req('remove_data', getargs={'target': 'user_base', 'username': username})
            if res.text != 'success':
                error_msgbox(res.text)
        load_search_results(self.ui.tableWidget, 'user_base', self.ordby_key, self.ordby_desc, {'type': 'visitor'})


class ViewStaff(QMainWindow):  # view/search/delete staff
    def __init__(self):
        super(ViewStaff, self).__init__()
        self.ui = view_s()
        self.ui.setupUi(self)
        center(self)
        self.show()
        load_search_results(self.ui.tableWidget, 'user_base', None, None, {'type': 'staff'})
        self.ui.pushButton.clicked.connect(self.searchStaff)
        self.ui.pushButton_2.clicked.connect(self.deleteStaff)

        self.ordby_key = None
        self.ordby_desc = None
        self.ui.tableWidget.horizontalHeader().sortIndicatorChanged.connect(self.switchSort)

        self.ui.pushButton_3.clicked.connect(self.goBack)

    def goBack(self):
        self.close()
        self.Open = AdminFunctionality()

    def switchSort(self, col_index, ord):
        self.ordby_key = col_order['user_base'][col_index]
        self.ordby_desc = (ord != QtCore.Qt.DescendingOrder)
        self.ui.tableWidget.setSortingEnabled(False)
        self.searchStaff()
        self.ui.tableWidget.setSortingEnabled(True)

    def searchStaff(self):
        getdata = {'type': 'staff'}
        if self.ui.lineEdit.text() != '':
            getdata['email'] = self.ui.lineEdit.text()
        if self.ui.lineEdit_2.text() != '':
            getdata['username'] = self.ui.lineEdit_2.text()
        load_search_results(self.ui.tableWidget, 'user_base', self.ordby_key, self.ordby_desc, getdata)


    def deleteStaff(self):
        rows = sorted(set(index.row() for index in self.ui.tableWidget.selectedIndexes()))
        for row in rows:
            username = self.ui.tableWidget.item(row, 0).text()
            res = make_req('remove_data', getargs={'target': 'user_base', 'username': username})
            if res.text != 'success':
                error_msgbox(res.text)
        load_search_results(self.ui.tableWidget, 'user_base', self.ordby_key, self.ordby_desc, {'type': 'staff'})


class AddAnimal(QMainWindow):  # add animal
    def __init__(self):
        super(AddAnimal, self).__init__()
        self.ui = add_animal()
        self.ui.setupUi(self)
        center(self)
        self.show()
        populate_combobox(self.ui.comboBox_2, 'exhibit', 'name', default_empty=False)
        self.ui.pushButton_2.clicked.connect(self.addAnimal)
        self.ui.pushButton_3.clicked.connect(self.goBack)

    def addAnimal(self):
        if self.ui.lineEdit.text() == '':
            error_msgbox('No animal name entered!')
            return
        if self.ui.lineEdit_2.text() == '':
            error_msgbox('No animal species entered!')
            return

        res = make_req('add_data',
                       getargs={'target': 'animal'},
                       postargs={'name': self.ui.lineEdit.text(),
                                 'species': self.ui.lineEdit_2.text(),
                                 'type': self.ui.comboBox.currentText(),
                                 'age': self.ui.spinBox.value(),
                                 'exhname': self.ui.comboBox_2.currentText()})
        if res.text != 'success':
            error_msgbox(res.text)
            return

        self.ui.lineEdit.setText('')
        self.ui.lineEdit_2.setText('')
        self.ui.comboBox.setCurrentIndex(0)
        self.ui.comboBox_2.setCurrentIndex(0)
        self.ui.spinBox.setValue(0)

    def goBack(self):
        self.close()
        self.Open = AdminFunctionality()


class AdminViewShows(QMainWindow):  # view/search/delete shows
    def __init__(self):
        super(AdminViewShows, self).__init__()
        self.ui = admin_view_shows()
        self.ui.setupUi(self)
        center(self)
        self.show()
        self.ui.pushButton.clicked.connect(self.searchShows)
        self.ui.pushButton_2.clicked.connect(self.deleteShow)
        self.rows = load_search_results(self.ui.tableWidget, 'exhibit_show', None, None)
        populate_combobox(self.ui.comboBox_2, 'exhibit', 'name')

        self.ui.tableWidget.setSortingEnabled(True)
        self.ordby_key = None
        self.ordby_desc = None
        self.ui.tableWidget.horizontalHeader().sortIndicatorChanged.connect(self.switchSort)

        self.ui.pushButton_3.clicked.connect(self.goBack)

    def goBack(self):
        self.close()
        self.Open = AdminFunctionality()

    def switchSort(self, col_index, ord):
        self.ordby_key = col_order['exhibit_show'][col_index]
        self.ordby_desc = (ord != QtCore.Qt.DescendingOrder)
        self.ui.tableWidget.setSortingEnabled(False)
        self.searchShows()
        self.ui.tableWidget.setSortingEnabled(True)


    def searchShows(self):
        showdate = self.ui.dateEdit.date().toPyDate()

        getdata = {}
        if self.ui.checkBox.isChecked():
            getdata['showtimeDay'] = str(showdate.day)
            getdata['showtimeMonth'] = str(showdate.month)
            getdata['showtimeYear'] = str(showdate.year)
        if self.ui.lineEdit.text() != '':
            getdata['name'] = self.ui.lineEdit.text()
        if self.ui.comboBox_2.currentText() != '':
            getdata['exhname'] = self.ui.comboBox_2.currentText()
        self.rows = load_search_results(self.ui.tableWidget, 'exhibit_show', self.ordby_key, self.ordby_desc, getdata)


    def deleteShow(self):
        rows = sorted(set(index.row() for index in self.ui.tableWidget.selectedIndexes()))
        for row in rows:
            res = make_req('remove_data', getargs={'target': 'exhibit_show',
                                                   'name': self.rows[row]['name'],
                                                   'showtime': self.rows[row]['showtime']})
            if res.text != 'success':
                error_msgbox(res.text)
        self.searchShows()


class AdminViewAnimals(QMainWindow):  # view/search/delete animals
    def __init__(self):
        super(AdminViewAnimals, self).__init__()
        self.ui = admin_view_animals()
        self.ui.setupUi(self)
        center(self)
        self.show()
        self.ui.pushButton.clicked.connect(self.searchAnimals)
        self.ui.pushButton_2.clicked.connect(self.deleteAnimal)
        self.rows = load_search_results(self.ui.tableWidget, 'animal', None, None)
        # populate_combobox(self.ui.comboBox, 'type', 'name', default_empty=False)
        populate_combobox(self.ui.comboBox_2, 'exhibit', 'name')

        self.ordby_key = None
        self.ordby_desc = None
        self.ui.tableWidget.horizontalHeader().sortIndicatorChanged.connect(self.switchSort)

        self.ui.pushButton_3.clicked.connect(self.goBack)

    def goBack(self):
        self.close()
        self.Open = AdminFunctionality()

    def switchSort(self, col_index, ord):
        self.ordby_key = col_order['animal'][col_index]
        self.ordby_desc = (ord != QtCore.Qt.DescendingOrder)
        self.ui.tableWidget.setSortingEnabled(False)
        self.searchAnimals()
        self.ui.tableWidget.setSortingEnabled(True)

    def searchAnimals(self):
        getdata = {}
        if self.ui.lineEdit.text() != '':
            getdata['name'] = self.ui.lineEdit.text()
        if self.ui.lineEdit_2.text() != '':
            getdata['species'] = self.ui.lineEdit_2.text()
        if self.ui.comboBox.currentText() != '':
            getdata['type'] = self.ui.comboBox.currentText()
        if self.ui.spinBox_2.value() != 0 and self.ui.spinBox.value() <= self.ui.spinBox_2.value():
            getdata['ageLo'] = self.ui.spinBox.value()
            getdata['ageHi'] = self.ui.spinBox_2.value()
        if self.ui.comboBox_2.currentText() != '':
            getdata['exhname'] = self.ui.comboBox_2.currentText()
        self.rows = load_search_results(self.ui.tableWidget, 'animal', self.ordby_key, self.ordby_desc, getdata)

    def deleteAnimal(self):
        rows = sorted(set(index.row() for index in self.ui.tableWidget.selectedIndexes()))
        for row in rows:
            res = make_req('remove_data', getargs={'target': 'animal',
                                                   'name': self.ui.tableWidget.item(row, 0).text(),
                                                   'species': self.ui.tableWidget.item(row, 1).text()})
            if res.text != 'success':
                error_msgbox(res.text)
        self.searchAnimals()


class AddShow(QMainWindow):  # add show
    def __init__(self):
        super(AddShow, self).__init__()
        self.ui = add_show()
        self.ui.setupUi(self)
        center(self)
        self.show()
        populate_combobox(self.ui.comboBox_2, 'exhibit', 'name', default_empty=False)
        populate_combobox(self.ui.comboBox_3, 'user_base', 'username',
                          default_empty=False, data_args={'type': 'staff'})
        self.ui.pushButton_2.clicked.connect(self.addShow)
        self.ui.pushButton_3.clicked.connect(self.goBack)

    def addShow(self):
        if self.ui.lineEdit.text() == '':
            error_msgbox('No show name entered!')
            return

        if re.match(r"\d{1,2}:\d{1,2}", self.ui.lineEdit_2.text()):
            hours_secs = self.ui.lineEdit_2.text() + ':00'
        elif re.match(r"\d{1,2}:\d{1,2}:\d{1,2}", self.ui.lineEdit_2.text()):
            hours_secs = self.ui.lineEdit_2.text()
        else:
            error_msgbox('Invalid time entered!')
            return

        res = make_req('add_data',
                       getargs={'target': 'exhibit_show'},
                       postargs={'name': self.ui.lineEdit.text(),
                                 'showtime': str(self.ui.dateEdit.date().toPyDate()) + ' ' + hours_secs,
                                 'exhname': self.ui.comboBox_2.currentText(),
                                 'hostname': self.ui.comboBox_3.currentText()})
        if res.text != 'success':
            error_msgbox(res.text)
            return

        self.ui.lineEdit.setText('')
        self.ui.lineEdit_2.setText('')
        self.ui.comboBox_2.setCurrentIndex(0)
        self.ui.comboBox_3.setCurrentIndex(0)

    def goBack(self):
        self.close()
        self.Open = AdminFunctionality()



def main():
    app = QtWidgets.QApplication(sys.argv)
    window = LoginForm()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()