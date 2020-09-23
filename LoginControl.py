# This Python file uses the following encoding: utf-8
import sys
import os

from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from PyQt5 import uic, QtWidgets


class Inbox(QtWidgets.QWidget):
    def __init__(self):
        super(Inbox, self).__init__()
        self.uic.loadUi('inbox.ui', self)
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    Inbox = Inbox()
    Inbox.setWindowTitle("Good Evening, Mr. Bond.")
    #Inbox.show()



    sys.exit(app.exec_())
