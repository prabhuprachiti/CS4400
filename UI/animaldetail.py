# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'animaldetail.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setInputMethodHints(QtCore.Qt.ImhUppercaseOnly)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(360, 50, 81, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(360, 90, 81, 16))
        self.label_2.setObjectName("label_2")
        self.name = QtWidgets.QLabel(self.centralwidget)
        self.name.setGeometry(QtCore.QRect(230, 180, 141, 16))
        self.name.setObjectName("name")
        self.species = QtWidgets.QLabel(self.centralwidget)
        self.species.setGeometry(QtCore.QRect(380, 180, 131, 16))
        self.species.setObjectName("species")
        self.age = QtWidgets.QLabel(self.centralwidget)
        self.age.setGeometry(QtCore.QRect(510, 180, 171, 16))
        self.age.setObjectName("age")
        self.exhibit = QtWidgets.QLabel(self.centralwidget)
        self.exhibit.setGeometry(QtCore.QRect(270, 260, 131, 16))
        self.exhibit.setObjectName("exhibit")
        self.type = QtWidgets.QLabel(self.centralwidget)
        self.type.setGeometry(QtCore.QRect(440, 260, 131, 16))
        self.type.setObjectName("type")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(20, 20, 93, 28))
        self.pushButton.setObjectName("pushButton")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "DBVizards"))
        self.label.setText(_translate("MainWindow", "Atlanta Zoo"))
        self.label_2.setText(_translate("MainWindow", "Animal Detail"))
        self.name.setText(_translate("MainWindow", "Name:"))
        self.species.setText(_translate("MainWindow", "Species:"))
        self.age.setText(_translate("MainWindow", "Age:"))
        self.exhibit.setText(_translate("MainWindow", "Exhibit:"))
        self.type.setText(_translate("MainWindow", "Type:"))
        self.pushButton.setText(_translate("MainWindow", "Back"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

