import os
import signal
import sys

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QAction
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QStackedWidget
from PyQt4.QtGui import QWidget

import qtUtils
from qChatWidget import QChatWidget
from qGroupChatWidget import QGroupChatWidget
from qConnectingWidget import QConnectingWidget
from qNickInputWidget import QNickInputWidget

from src.hinge.utils import errors


class QChatTab(QWidget):
    def __init__(self, chatWindow, nick='', justAccepted=False, isGroup=False):
        QWidget.__init__(self)

        self.chatWindow = chatWindow
        self.nick = nick
        self.justAccepted = justAccepted
        self.isGroup = isGroup
        self.unreadCount = 0

        self.widgetStack = QStackedWidget(self)
        self.widgetStack.addWidget(QNickInputWidget('new_chat.png', 150, self.connectClicked, parent=self))
        self.widgetStack.addWidget(QConnectingWidget(parent=self))
        self.widgetStack.addWidget(QChatWidget(self.chatWindow.connectionManager, nick=nick, parent=self))
        self.widgetStack.addWidget(QGroupChatWidget(self.chatWindow.connectionManager, nick=nick, parent=self))

        # Skip the chat layout if the nick was given denoting an incoming connection
        if self.nick is None or self.nick == '' and isGroup is False:
            self.widgetStack.setCurrentIndex(0)
        elif self.nick != '' or self.nick is not None or isGroup is True:
            if isGroup is True:
                if self.justAccepted is False:
                    self.widgetStack.setCurrentIndex(3)
                    self.widgetStack.widget(3).isGroupPopup()
                else:
                    self.widgetStack.setCurrentIndex(3)
                    self.widgetStack.widget(3).isGroupPopup(True)
            else:
                self.widgetStack.setCurrentIndex(2)

        layout = QHBoxLayout()
        layout.addWidget(self.widgetStack)
        self.setLayout(layout)

    def connectClicked(self, nick):
        # Check that the nick isn't already connected
        if self.chatWindow.isNickInTabs(nick):
            QMessageBox.warning(self, errors.TITLE_ALREADY_CONNECTED, errors.ALREADY_CONNECTED % (nick))
            return

        self.nick = nick
        self.widgetStack.widget(1).setConnectingToNick(self.nick)
        self.widgetStack.setCurrentIndex(1)
        self.chatWindow.connectionManager.openChat(self.nick)

    def showNowChattingMessage(self):
        if self.isGroup:
            self.widgetStack.widget(3).delAddUser()
            self.widgetStack.widget(3).showNowChattingMessage(self.nick)
        else:
            self.widgetStack.setCurrentIndex(2)
            self.widgetStack.widget(2).showNowChattingMessage(self.nick)

    def appendMessage(self, message, source):
        if self.isGroup:
            self.widgetStack.widget(3).appendMessage(message, source)
        else:
            self.widgetStack.widget(2).appendMessage(message, source)


    def resetOrDisable(self):
        # If the connecting widget is showing, reset to the nick input widget
        # If the chat widget is showing, disable it to prevent sending of more messages
        curWidgetIndex = self.widgetStack.currentIndex()
        if curWidgetIndex == 1:
            self.widgetStack.setCurrentIndex(0)
        elif curWidgetIndex == 2:
            self.widgetStack.widget(2).disable()


    def enable(self):
        self.widgetStack.setCurrentIndex(2)
        self.widgetStack.widget(2).enable()
