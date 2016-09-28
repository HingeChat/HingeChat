import os
import signal

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QVBoxLayout

from qNickInputWidget import QNickInputWidget
from qLinkLabel import QLinkLabel
import qtUtils

from src.hinge.utils import constants
from src.hinge.utils import utils

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

        loginWindow = QLoginWindow(parent, nick)
        loginWindow.exec_()
        return loginWindow.nick
