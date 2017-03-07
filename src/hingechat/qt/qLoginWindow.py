import os
import signal

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout

from src.hingechat.qt.qNickInputWidget import QNickInputWidget
from src.hingechat.qt.qLinkLabel import QLinkLabel
from src.hingechat.qt import qtUtils
from src.hinge.utils import *


class QLoginWindow(QDialog):

    def __init__(self, parent, nick=""):
        QDialog.__init__(self, parent)
        self.nick = None

        # Set the title and icon
        self.setWindowTitle("HingeChat")
        self.setWindowIcon(QIcon(qtUtils.getAbsoluteImagePath('icon.png')))

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(QNickInputWidget('splash_icon.png', 200, self.connectClicked, nick, self))
        vbox.addStretch(1)

        self.setLayout(vbox)

        qtUtils.resizeWindow(self, 500, 200)
        qtUtils.centerWindow(self)

    def connectClicked(self, nick):
        self.nick = nick
        self.close()

    @staticmethod
    def getNick(parent, nick=""):
        if nick is None:
            nick = ""
        else:
            pass
        loginWindow = QLoginWindow(parent, nick)
        loginWindow.exec_()
        return loginWindow.nick
