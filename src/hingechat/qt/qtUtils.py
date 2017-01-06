import os
import signal

from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import QDesktopWidget
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QInputDialog
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QPixmap
from PyQt4.QtGui import QWidget

from qPassphraseDialog import QPassphraseDialog

from src.hinge.utils import constants
from src.hinge.utils import utils

def centerWindow(window):
    centerPoint = QDesktopWidget().availableGeometry().center()
    geo = window.frameGeometry()
    geo.moveCenter(centerPoint)
    window.move(geo.topLeft())

def resizeWindow(window, width, height):
    window.setGeometry(0, 0, width, height)

def showDesktopNotification(systemTrayIcon, title, message):
    systemTrayIcon.showMessage(title, message)

isLightTheme = False

def setIsLightTheme(color):
    global isLightTheme
    isLightTheme = (color.red() > 100 and color.blue() > 100 and color.green() > 100)

def getAbsoluteImagePath(imageName, root=False):
    global isLightTheme
    if root:
        return utils.getAbsoluteResourcePath('images/' + imageName)
    return utils.getAbsoluteResourcePath('images/' + ('light' if isLightTheme else 'dark') + '/' + imageName)

def exitApp(systemTrayIcon=None):
    if systemTrayIcon != None:
        systemTrayIcon.hide()
    os.kill(os.getpid(), signal.SIGINT)