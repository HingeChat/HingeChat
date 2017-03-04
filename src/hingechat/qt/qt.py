import sys
import time

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QWidget

from src.hinge.network.Client import Client
from src.hingechat.network import qtThreads
from src.hingechat.qt import qtUtils
from src.hingechat.qt.qAcceptDialog import QAcceptDialog
from src.hingechat.qt.qChatWindow import QChatWindow
from src.hingechat.qt.qLoginWindow import QLoginWindow
from src.hingechat.qt.qWaitingDialog import QWaitingDialog
from src.hinge.utils import *


class QtUI(QApplication):

    def __init__(self, argv, nick, turn, port):
        QApplication.__init__(self, argv)

        self.nick = nick
        self.turn = turn
        self.port = port
        self.event_loop_running = False

        self.client = None
        self.chat_window = None
        self.waiting_dialog = None

        qtUtils.setIsLightTheme(self.palette().color(QPalette.Window))

        self.aboutToQuit.connect(self.stop)

    def start(self):
        self.timer = QTimer()
        self.timer.start(500)
        self.timer.timeout.connect(lambda: None)

        nick = QLoginWindow.getNick(QWidget(), self.nick)
        if nick is None:
            qtUtils.exitApp()
        else:
            self.nick = str(nick)

        self.chat_window = QChatWindow(self.restart)
        self.chat_window.show()

        self.__connectToServer()

        if not self.event_loop_running:
            self.event_loop_running = True
            self.exec_()

    def stop(self):
        if self.client:
            self.client.disconnectFromServer()

        time.sleep(0.25)
        
        if self.chat_window:
            self.chat_window.exit()

    def restart(self):
        if self.client:
            self.client.disconnectFromServer()

        self.closeAllWindows()
        if self.chat_window:
            self.chat_window = None

        self.start()

    def __connectToServer(self):
        callbacks = {
            'recv': self.chat_window.postMessage,
            'new': self.chat_window.newClient,
            'handshake': self.chat_window.clientReady,
            'smp': self.chat_window.smpRequest,
            'err': self.chat_window.handleError
        }
        
        self.client = Client(self.nick, (self.turn, self.port), callbacks)
        self.chat_window.client = self.client

        self.connect_thread = qtThreads.QtServerConnectThread(self.client, self.__postConnect, self.__connectFailure)
        self.connect_thread.start()

        self.waiting_dialog = QWaitingDialog(self.chat_window, "Connecting to server...")
        self.waiting_dialog.show()

    @pyqtSlot()
    def __postConnect(self):
        self.waiting_dialog.close()
        self.chat_window.connectedToServer()

    @pyqtSlot(str)
    def __connectFailure(self, error_message):
        if 'Errno 111' in error_message:
            error_message = "Unable to contact the server. Try again later."
        QMessageBox.critical(self.chatWindow, FAILED_TO_CONNECT, error_message)
        self.restart()
