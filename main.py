# This Python file uses the following encoding: utf-8
import sys
import os

from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from PyQt5 import uic, QtWidgets
from LoginControl import Inbox

class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super(LoginWindow, self).__init__()
        uic.loadUi('login.ui', self)
        self.button = self.findChild(QtWidgets.QPushButton, "pushButton_2")
        self.button.clicked.connect(self.action1)
        self.button2 = self.findChild(QtWidgets.QPushButton, "pushButton")
        self.button2.clicked.connect(self.action2)
        self.show()




    def action1(self):
        Inbox(QtWidgets.Qwidget)
        Inbox.show()

    def action2(self):
        print("HOLA, AMIGOS!")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    LoginWindow = LoginWindow()
    LoginWindow.setWindowTitle("Group 2 Email Application")
    #LoginWindow.show()

    sys.exit(app.exec_())

    # loader = QUiLoader()
    #  path = self.properfile("inbox.ui")
    #  ui_file = QFile(path)
    #  ui_file.open(QFile.ReadOnly)
    #   loader.load(ui_file, self)
    #  push1 = ui_file.pushButton_2
    # push1.clicked.connect(self.action1)
    #   ui_file.close()