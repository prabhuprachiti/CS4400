# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'registration.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):

    def setupUi(self, DBVizards):
        DBVizards.setObjectName("DBVizards")
        DBVizards.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(DBVizards)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(200, 110, 55, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(200, 150, 71, 16))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(200, 190, 71, 16))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(200, 230, 111, 16))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(320, 60, 111, 16))
        self.label_5.setObjectName("label_5")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(320, 110, 113, 22))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_2.setGeometry(QtCore.QRect(320, 150, 113, 22))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_3 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_3.setGeometry(QtCore.QRect(320, 190, 113, 22))
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.lineEdit_4 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_4.setGeometry(QtCore.QRect(320, 230, 113, 22))
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(260, 300, 93, 28))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(390, 300, 93, 28))
        self.pushButton_2.setObjectName("pushButton_2")
        DBVizards.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(DBVizards)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        DBVizards.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(DBVizards)
        self.statusbar.setObjectName("statusbar")
        DBVizards.setStatusBar(self.statusbar)

        self.retranslateUi(DBVizards)
        QtCore.QMetaObject.connectSlotsByName(DBVizards)

    def retranslateUi(self, DBVizards):
        _translate = QtCore.QCoreApplication.translate
        DBVizards.setWindowTitle(_translate("DBVizards", "DBVizards"))
        self.label.setText(_translate("DBVizards", "Email"))
        self.label_2.setText(_translate("DBVizards", "Username"))
        self.label_3.setText(_translate("DBVizards", "Password"))
        self.label_4.setText(_translate("DBVizards", "Confirm Password"))
        self.label_5.setText(_translate("DBVizards", "Atlanta Zoo"))
        self.pushButton.setText(_translate("DBVizards", "Register Visitor"))
        self.pushButton_2.setText(_translate("DBVizards", "Register Staff"))


    def openWindow(self):
        self.window = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)
        self.window.show()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    DBVizards = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(DBVizards)
    DBVizards.show()
    sys.exit(app.exec_())

