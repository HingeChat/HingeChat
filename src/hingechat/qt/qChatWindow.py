import os
import signal
import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QSplitter
from PyQt5.QtWidgets import QSystemTrayIcon
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QToolBar
from PyQt5.QtWidgets import QToolButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from src.hingechat.qt.qChatTab import QChatTab
from src.hingechat.qt.qAcceptDialog import QAcceptDialog
from src.hingechat.qt.qSMPInitiateDialog import QSMPInitiateDialog
from src.hingechat.qt.qSMPRespondDialog import QSMPRespondDialog
from src.hingechat.qt import qtUtils
from src.hinge.utils import *


class QChatWindow(QMainWindow):

    new_client_signal = pyqtSignal(str)
    client_ready_signal = pyqtSignal(str)
    smp_request_signal = pyqtSignal(int, str, str, int)
    handle_error_signal = pyqtSignal(int, int)
    send_message_signal = pyqtSignal(str, str, str)

    def __init__(self, restart_callback, client=None, message_queue=None):
        QMainWindow.__init__(self)

        self.restart_callback = restart_callback
        self.client = client
        self.message_queue = message_queue

        self.new_client_signal.connect(self.newClientSlot)
        self.client_ready_signal.connect(self.clientReadySlot)
        self.smp_request_signal.connect(self.smpRequestSlot)
        self.handle_error_signal.connect(self.handleErrorSlot)
        self.send_message_signal.connect(self.sendMessageToTab)

        self.chat_tabs = QTabWidget(self)
        self.chat_tabs.setTabsClosable(True)
        self.chat_tabs.setMovable(True)
        self.chat_tabs.tabCloseRequested.connect(self.closeTab)
        self.chat_tabs.currentChanged.connect(self.tabChanged)

        self.status_bar = self.statusBar()

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(qtUtils.getAbsoluteImagePath('icon.ico', True)))
        self.tray_icon.setToolTip("HingeChat")

        self.tray_menu = QMenu()
        self.exit_action = QAction("Exit", self, shortcut="Ctrl+Q", statusTip="Exit", triggered=self.exit)
        self.exit_action.setIcon(QIcon(qtUtils.getAbsoluteImagePath('exit.png')))
        self.tray_menu.addAction(self.exit_action)
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.setVisible(True)

        self.__setMenubar()

        vbox = QVBoxLayout()
        vbox.addWidget(self.chat_tabs)

        self.central_widget = QWidget()
        self.central_widget.setLayout(vbox)
        self.setCentralWidget(self.central_widget)

        qtUtils.resizeWindow(self, 700, 400)
        qtUtils.centerWindow(self)

        self.setWindowTitle("HingeChat")
        self.setWindowIcon(QIcon(qtUtils.getAbsoluteImagePath('icon.png')))

    def exit(self):
        qtUtils.exitApp(self.tray_icon)

    def connectedToServer(self):
        self.addNewTab()

    def newClient(self, remote_id):
        self.new_client_signal.emit(remote_id)

    @pyqtSlot(str)
    def newClientSlot(self, remote_id):
        nick = self.client.getClientNick(remote_id)

        if not self.isActiveWindow():
            qtUtils.showDesktopNotification(self.tray_icon, "Chat request from %s" % nick, '')

        accept = QAcceptDialog.getAnswer(self, nick)
        if not accept:
            self.client.newClientRejected(remote_id)
            return

        if self.isNickInTabs(nick):
            self.getTabByNick(nick)[0].enable()
        else:
            self.addNewTab(nick)

        self.client.newClientAccepted(remote_id)

    def addNewTab(self, nick=None):
        new_tab = QChatTab(self, nick)
        if nick is None:
            self.chat_tabs.addTab(new_tab, "New Chat")
        else:
            self.chat_tabs.addTab(new_tab, nick)
        self.chat_tabs.setCurrentWidget(new_tab)
        new_tab.setFocus()

    def clientReady(self, remote_id):
        self.client_ready_signal.emit(remote_id)

    @pyqtSlot(str)
    def clientReadySlot(self, remote_id):
        nick = self.client.getClientNick(remote_id)

        tab, tab_index = self.getTabByNick(nick)
        self.chat_tabs.setTabText(tab_index, nick)
        tab.showNowChattingMessage()

        if tab_index == self.chat_tabs.currentIndex():
            self.setWindowTitle(nick)

    def smpRequest(self, callback_type, client_id, question='', errno=0):
        self.smp_request_signal.emit(callback_type, client_id, question, errno)

    @pyqtSlot(int, str, str, int)
    def smpRequestSlot(self, callback_type, client_id, question='', errno=0):
        if callback_type == SMP_CALLBACK_REQUEST:
            answer, clicked = QSMPRespondDialog.getAnswer(client_id, question)
            if clicked == BUTTON_OKAY:
                self.client.respondSmp(client_id, str(answer))
        elif callback_type == SMP_CALLBACK_COMPLETE:
            QMessageBox.information(self, "%s Authenticated" % nick,
                "Your chat session with %s has been succesfully authenticated. The conversation is verfied as secure." % nick)
        elif callback_type == SMP_CALLBACK_ERROR:
            if errno == ERR_SMP_CHECK_FAILED:
                QMessageBox.warning(self, TITLE_PROTOCOL_ERROR, PROTOCOL_ERROR % (nick))
            elif errno == ERR_SMP_MATCH_FAILED:
                QMessageBox.critical(self, TITLE_SMP_MATCH_FAILED, SMP_MATCH_FAILED)

    def handleError(self, client_id, errno):
        self.handle_error_signal.emit(client_id, errno)

    @pyqtSlot(int, int)
    def handleErrorSlot(self, client_id, errno):
        nick = self.client.nick
        if nick == '':
            # If no nick was given, disable all tabs
            self.__disableAllTabs()
        else:
            try:
                tab = self.getTabByNick(nick)[0]
                tab.resetOrDisable()
            except:
                tab = self.getTabByText("New Chat")
                if hasattr(tab, 'resetOrDisable'):
                    tab.resetOrDisable()

        if errno == ERR_CONN_ENDED:
            QMessageBox.warning(self, TITLE_CONNECTION_ENDED, CONNECTION_ENDED % (nick))
        elif errno == ERR_NICK_NOT_FOUND:
            QMessageBox.information(self, TITLE_NICK_NOT_FOUND, NICK_NOT_FOUND % (nick))
            if hasattr(tab, 'nick'):
                tab.nick = None
        elif errno == ERR_CONN_REJECTED:
            QMessageBox.warning(self, TITLE_CONNECTION_REJECTED, CONNECTION_REJECTED % (nick))
            if hasattr(tab, 'nick'):
                tab.nick = None
        elif errno == ERR_BAD_HANDSHAKE:
            QMessageBox.warning(self, TITLE_PROTOCOL_ERROR, PROTOCOL_ERROR % (nick))
        elif errno == ERR_CLIENT_EXISTS:
            QMessageBox.information(self, TITLE_CLIENT_EXISTS, CLIENT_EXISTS % (nick))
        elif errno == ERR_SELF_CONNECT:
            QMessageBox.warning(self, TITLE_SELF_CONNECT, SELF_CONNECT)
        elif errno == ERR_SERVER_SHUTDOWN:
            QMessageBox.critical(self, TITLE_SERVER_SHUTDOWN, SERVER_SHUTDOWN)
        elif errno == ERR_ALREADY_CONNECTED:
            QMessageBox.information(self, TITLE_ALREADY_CONNECTED, ALREADY_CONNECTED % (nick))
        elif errno == ERR_INVALID_COMMAND:
            QMessageBox.warning(self, TITLE_INVALID_COMMAND, INVALID_COMMAND % (nick))
        elif errno == ERR_NETWORK_ERROR:
            QMessageBox.critical(self, TITLE_NETWORK_ERROR, NETWORK_ERROR)
        elif errno == ERR_BAD_HMAC:
            QMessageBox.critical(self, TITLE_BAD_HMAC, BAD_HMAC)
        elif errno == ERR_BAD_DECRYPT:
            QMessageBox.warning(self, TITLE_BAD_DECRYPT, BAD_DECRYPT)
        elif errno == ERR_KICKED:
            QMessageBox.critical(self, TITLE_KICKED, KICKED)
        elif errno == ERR_NICK_IN_USE:
            QMessageBox.warning(self, TITLE_NICK_IN_USE, NICK_IN_USE)
            self.restartCallback()
        elif errno == ERR_MESSAGE_REPLAY:
            QMessageBox.critical(self, TITLE_MESSAGE_REPLAY, MESSAGE_REPLAY)
        elif errno == ERR_MESSAGE_DELETION:
            QMessageBox.critical(self, TITLE_MESSAGE_DELETION, MESSAGE_DELETION)
        elif errno == ERR_PROTOCOL_VERSION_MISMATCH:
            QMessageBox.critical(self, TITLE_PROTOCOL_VERSION_MISMATCH, PROTOCOL_VERSION_MISMATCH)
            self.restartCallback()
        else:
            QMessageBox.warning(self, TITLE_UNKNOWN_ERROR, UNKNOWN_ERROR % (nick))

    def __disableAllTabs(self):
        for i in range(0, self.chat_tabs.count()):
            cur_tab = self.chat_tabs.widget(i)
            cur_tab.resetOrDisable()

    def postMessage(self, command, client_id, data):
        self.send_message_signal.emit(command, client_id, data)

    @pyqtSlot(str, str, str)
    def sendMessageToTab(self, command, remote_id, data):
        nick = self.client.getClientNick(remote_id)
        tab, tab_index = self.getTabByNick(nick)
        if command == COMMAND_TYPING:
            if tab_index == self.chat_tabs.currentIndex():
                data = int(data)
                if data == TYPING_START:
                    self.status_bar.showMessage("%s is typing" % nick)
                elif data == TYPING_STOP_WITHOUT_TEXT:
                    self.status_bar.showMessage('')
                elif data == TYPING_STOP_WITH_TEXT:
                    self.status_bar.showMessage("%s has entered text" % nick)
        elif command == COMMAND_SMP_0:
            print(('got request for smp in tab %d' % (tab_index)))
        else:
            tab.appendMessage(data, MSG_RECEIVER)

            if tab_index != self.chat_tabs.currentIndex():
                tab.unreadCount += 1
                self.chat_tabs.setTabText(tab_index, "%s (%d)" % (tab.nick, tab.unread_count))
            else:
                self.status_bar.showMessage('')

            chat_log_scrollbar = tab.widget_stack.widget(2).chatLog.verticalScrollBar()
            if not self.isActiveWindow() or tab_index != self.chat_tabs.currentIndex() or \
               chat_log_scrollbar.value() != chatLogScrollbar.maximum():
                qtUtils.showDesktopNotification(self.tray_icon, nick, data)

    @pyqtSlot(int)
    def tabChanged(self, index):
        tab = self.chat_tabs.widget(index)

        if (tab is None) or (tab.nick is None):
            self.setWindowTitle("HingeChat")
        else:
            self.setWindowTitle(tab.nick)

        if (tab is not None) and (tab.unread_count != 0):
            tab.unread_count = 0
            self.chat_tabs.setTabText(index, tab.nick)

    @pyqtSlot(int)
    def closeTab(self, index):
        tab = self.chat_tabs.widget(index)
        self.client.closeSession(tab.nick)

        self.chatTabs.removeTab(index)

        if self.chat_tabs.count() == 0:
            self.addNewTab()

    def getTabByText(self, tab):
        for i in range(0, self.chat_tabs.count()):
            tab_text = self.chat_tabs.tabText(i)
            if tab_text == tab:
                which_tab = i
                cur_tab = self.chat_tabs.widget(which_tab)
                return (cur_tab, which_tab)
        return None

    def getTabByNick(self, nick):
        for i in range(0, self.chat_tabs.count()):
            cur_tab = self.chat_tabs.widget(i)
            if cur_tab.nick == nick:
                return (cur_tab, i)
        return None

    def isNickInTabs(self, nick):
        for i in range(0, self.chat_tabs.count()):
            cur_tab = self.chat_tabs.widget(i)
            if cur_tab.nick == nick:
                return True
        return False

    def __setMenubar(self):
        new_chat_icon = QIcon(qtUtils.getAbsoluteImagePath('new_chat.png'))
        exit_icon = QIcon(qtUtils.getAbsoluteImagePath('exit.png'))
        menu_icon = QIcon(qtUtils.getAbsoluteImagePath('menu.png'))

        new_chat_action = QAction(new_chat_icon, '&New chat', self)
        auth_chat_action = QAction(new_chat_icon, '&Authenticate chat', self)
        exit_action = QAction(exit_icon, '&Exit', self)

        new_chat_action.triggered.connect(self.addNewTab)
        auth_chat_action.triggered.connect(self.__showAuthDialog)
        exit_action.triggered.connect(self.__exit)

        new_chat_action.setShortcut('Ctrl+N')
        exit_action.setShortcut('Ctrl+Q')

        options_menu = QMenu()
        options_menu.addAction(new_chat_action)
        options_menu.addAction(auth_chat_action)
        options_menu.addAction(exit_action)

        options_menu_button = QToolButton()
        new_chat_button = QToolButton()
        exit_button = QToolButton()

        new_chat_button.clicked.connect(self.addNewTab)
        exit_button.clicked.connect(self.__exit)

        options_menu_button.setIcon(menu_icon)
        new_chat_button.setIcon(new_chat_icon)
        exit_button.setIcon(exit_icon)

        options_menu_button.setMenu(options_menu)
        options_menu_button.setPopupMode(QToolButton.InstantPopup)

        toolbar = QToolBar(self)
        toolbar.addWidget(options_menu_button)
        toolbar.addWidget(new_chat_button)
        toolbar.addWidget(exit_button)
        self.addToolBar(Qt.LeftToolBarArea, toolbar)

    def __showAuthDialog(self):
        client = self.client.getClient(self.chat_tabs.currentWidget().nick)

        if client is None:
            QMessageBox.information(self, "Not Available", "You must be chatting with someone before you can authenticate the connection.")
            return

        try:
            question, answer, clicked = QSMPInitiateDialog.getQuestionAndAnswer()
        except AttributeError:
            QMessageBox.information(self, "Not Available", "Encryption keys are not available until you are chatting with someone")

        if clicked == BUTTON_OKAY:
            client.initiateSMP(str(question), str(answer))

    def __exit(self):
        if QMessageBox.Yes == QMessageBox.question(self, "Confirm Exit", "Are you sure you want to exit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No):
            self.exit()
