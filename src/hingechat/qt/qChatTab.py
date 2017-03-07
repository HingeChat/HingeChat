import os
import signal
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QStackedWidget
from PyQt5.QtWidgets import QWidget

from src.hingechat.qt import qtUtils
from src.hingechat.qt.qChatWidget import QChatWidget
from src.hingechat.qt.qConnectingWidget import QConnectingWidget
from src.hingechat.qt.qNickInputWidget import QNickInputWidget

from src.hinge.utils import *


class QChatTab(QWidget):

    def __init__(self, chat_window, nick=None, just_accepted=False):
        QWidget.__init__(self)

        self.chat_window = chat_window
        self.nick = nick
        self.just_accepted = just_accepted
        self.unread_count = 0

        self.widget_stack = QStackedWidget(self)
        self.widget_stack.addWidget(QNickInputWidget('new_chat.png', 150, self.connectClicked, parent=self))
        self.widget_stack.addWidget(QConnectingWidget(parent=self))
        self.widget_stack.addWidget(QChatWidget(self.chat_window.client, nick=nick, parent=self))

        if self.nick is not None:
            self.widget_stack.setCurrentIndex(2)
        else:
            self.widget_stack.setCurrentIndex(0)

        layout = QHBoxLayout()
        layout.addWidget(self.widget_stack)
        self.setLayout(layout)

    def connectClicked(self, nick):
        if self.chat_window.isNickInTabs(nick):
            QMessageBox.warning(self, TITLE_ALREADY_CONNECTED, ALREADY_CONNECTED % (nick))
            return

        self.nick = nick
        self.widget_stack.widget(1).setConnectingToNick(self.nick)
        self.widget_stack.setCurrentIndex(1)
        self.chat_window.client.openSession(self.nick)

    def appendMessage(self, message, source):
        self.widget_stack.widget(2).appendMessage(message, source)

    def showNowChattingMessage(self):
        self.widget_stack.setCurrentIndex(2)
        self.widget_stack.widget(2).showNowChattingMessage(self.nick)

    def enable(self):
        self.widget_stack.setCurrentIndex(2)
        self.widget_stack.widget(2).enable()

    def resetOrDisable(self):
        cur_widget_index = self.widget_stack.currentIndex()
        if cur_widget_index == 1:
            self.widget_stack.setCurrentIndex(0)
        elif cur_widget_index == 2:
            self.widget_stack.widget(2).disable()
