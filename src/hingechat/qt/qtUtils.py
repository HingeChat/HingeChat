import os
import signal

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QDesktopWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget

from src.hinge.utils import *


is_light_theme = False


def centerWindow(window):
    centerPoint = QDesktopWidget().availableGeometry().center()
    geo = window.frameGeometry()
    geo.moveCenter(centerPoint)
    window.move(geo.topLeft())


def resizeWindow(window, width, height):
    window.setGeometry(0, 0, width, height)


def showDesktopNotification(tray_icon, title, message):
    tray_icon.showMessage(title, message)


def setIsLightTheme(color):
    global is_light_theme
    is_light_theme = (color.red() > 100 and color.blue() > 100 and color.green() > 100)


def getAbsoluteImagePath(imageName, root=False):
    global is_light_theme
    if root:
        return getAbsoluteResourcePath('images/' + imageName)
    else:
        return getAbsoluteResourcePath('images/' + ('light' if is_light_theme else 'dark') + '/' + imageName)


def exitApp(tray_icon=None):
    if tray_icon is not None:
        tray_icon.hide()
    os.kill(os.getpid(), signal.SIGINT)
