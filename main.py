import sys
from PyQt5.QtWidgets import (QApplication, QLabel, QLineEdit,
                             QVBoxLayout, QWidget, QPushButton, QStackedWidget)
from PyQt5 import QtCore


stack = QStackedWidget
stack.

class LoginWindow(QWidget):
    def __init__(self):         ## another class called self
        super().__init__()      ## to inherit from base class and get QWidget

        self.setGeometry(0, 0, 800, 500)  ## xy of window, xy size
        self.setWindowTitle('Email Client')


        userName = QLabel(self)
        userNameBox = QLineEdit(self)
        passWord = QLabel(self)
        passWordBox = QLineEdit(self)
        passWordBox.setEchoMode(QLineEdit.Password)
        loginButton = QPushButton(self)
        loginButton.setText("Login")


        userName.setText("User name: ")
        passWord.setText("Password: ")

        userNameBox.move(self.geometry().center().x(), self.geometry().center().y()-100)
        userName.move(userNameBox.geometry().x()-75, userNameBox.geometry().y())
        passWordBox.move(userNameBox.geometry().x(), userNameBox.geometry().y()+30)
        passWord.move(passWordBox.geometry().x()-68, passWordBox.geometry().y())
        loginButton.move(passWord.geometry().x()+40, passWord.geometry().y()+30)



        self.show()


def main():
    app = QApplication(sys.argv)
    ex = LoginWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()