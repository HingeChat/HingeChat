import re

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QSplitter
from PyQt5.QtWidgets import QTextBrowser
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QWidget

from src.hingechat.qt import qtUtils
from src.hinge.utils import *


class QChatWidget(QWidget):

    def __init__(self, chat_window, nick, parent=None):
        QWidget.__init__(self, parent)

        self.chat_window = chat_window
        self.nick = nick

        self.disabled = False
        self.cleared = False

        self.urlRegex = re.compile(URL_REGEX)

        self.chatLog = QTextBrowser()
        self.chatLog.setOpenExternalLinks(True)

        self.chatInput = QTextEdit()
        self.chatInput.textChanged.connect(self.chatInputTextChanged)

        self.sendButton = QPushButton("Send")
        self.sendButton.clicked.connect(self.sendMessage)

        # Set the min height for the chatlog and a matching fixed height for the send button
        chatInputFontMetrics = QFontMetrics(self.chatInput.font())
        self.chatInput.setMinimumHeight(chatInputFontMetrics.lineSpacing() * 3)
        self.sendButton.setFixedHeight(chatInputFontMetrics.lineSpacing() * 3)

        hbox = QHBoxLayout()
        hbox.addWidget(self.chatInput)
        hbox.addWidget(self.sendButton)

        # Put the chatinput and send button in a wrapper widget so they may be added to the splitter
        chatInputWrapper = QWidget()
        chatInputWrapper.setLayout(hbox)
        chatInputWrapper.setMinimumHeight(chatInputFontMetrics.lineSpacing() * 3.7)

        # Put the chat log and chat input into a splitter so the user can resize them at will
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.chatLog)
        splitter.addWidget(chatInputWrapper)
        splitter.setSizes([int(parent.height()), 1])

        hbox = QHBoxLayout()
        hbox.addWidget(splitter)
        self.setLayout(hbox)

        self.typingTimer = QTimer()
        self.typingTimer.setSingleShot(True)
        self.typingTimer.timeout.connect(self.stoppedTyping)

    def setRemoteNick(self, nick):
        self.nick = nick

    def chatInputTextChanged(self):
        # Check if the text changed was the text box being cleared to avoid sending an invalid typing status
        if self.cleared:
            self.cleared = False
            return

        if str(self.chatInput.toPlainText())[-1:] == '\n':
            self.sendMessage()
        else:
            # Start a timer to check for the user stopping typing
            self.typingTimer.start(TYPING_TIMEOUT)
            self.sendTypingStatus(TYPING_START)

    def stoppedTyping(self):
        self.typingTimer.stop()
        if str(self.chatInput.toPlainText()) == '':
            self.sendTypingStatus(TYPING_STOP_WITHOUT_TEXT)
        else:
            self.sendTypingStatus(TYPING_STOP_WITH_TEXT)

    def sendMessage(self):
        if self.disabled:
            return
        else:
            pass

        self.typingTimer.stop()

        text = str(self.chatInput.toPlainText())[:-1]

        # Don't send empty messages
        if text == '':
            return

        # Convert URLs into clickable links
        text = self.__linkify(text)

        # Add the message to the message queue to be sent
        self.chat_window.client.getSession(self.remote_id).sendChatMessage(text)

        # Clear the chat input
        self.wasCleared = True
        self.chatInput.clear()

        self.appendMessage(text, MSG_SENDER)

    def sendTypingStatus(self, status):
        self.chat_window.client.getSession(self.remote_id).sendTypingMessage(status)

    def showNowChattingMessage(self, nick):
        self.nick = nick
        self.remote_id = self.chat_window.client.getClientId(self.nick)
        self.appendMessage("You are now securely chatting with " + self.nick + " :)",
                           MSG_SERVICE, show_timestamp_and_nick=False)

        self.appendMessage("It's a good idea to verify the communcation is secure by selecting "
                           "\"authenticate buddy\" in the options menu.", MSG_SERVICE, show_timestamp_and_nick=False)

        self.addNickButton = QPushButton('Add', self)
        self.addNickButton.setGeometry(584, 8, 31, 23)
        self.addNickButton.clicked.connect(self.addNickScreen)
        self.addNickButton.show()

    def addUser(self, user):
        nick = str(user.text()).lower()

        # Validate the given nick
        nickStatus = utils.isValidNick(nick)
        if nickStatus == errors.VALID_NICK:
            # TODO: Group chats
            pass
        elif nickStatus == errors.INVALID_NICK_CONTENT:
            QMessageBox.warning(self, errors.TITLE_INVALID_NICK, errors.INVALID_NICK_CONTENT)
        elif nickStatus == errors.INVALID_NICK_LENGTH:
            QMessageBox.warning(self, errors.TITLE_INVALID_NICK, errors.INVALID_NICK_LENGTH)
        elif nickStatus == errors.INVALID_EMPTY_NICK:
            QMessageBox.warning(self, errors.TITLE_EMPTY_NICK, errors.EMPTY_NICK)

    def addNickScreen(self):
        self.chatLog.setEnabled(False)
        self.chatInput.setEnabled(False)
        self.sendButton.setEnabled(False)
        self.addNickButton.hide()
        self.addUserText = QLabel("Enter a username to add a user to the group chat.", self)
        self.addUserText.setGeometry(200, 20, 300, 100)
        self.addUserText.show()
        self.user = QLineEdit(self)
        self.user.setGeometry(200, 120, 240, 20)
        self.user.returnPressed.connect(self.addUser)
        self.user.show()
        self.addUserButton = QPushButton('Add User', self)
        self.addUserButton.setGeometry(250, 150, 150, 25)
        self.addUserButton.clicked.connect(lambda: self.addUser(self.user))
        self.addUserButton.show()
        self.cancel = QPushButton('Cancel', self)
        self.cancel.setGeometry(298, 210, 51, 23)
        self.cancel.clicked.connect(lambda: self.chatLog.setEnabled(True))
        self.cancel.clicked.connect(lambda: self.chatInput.setEnabled(True))
        self.cancel.clicked.connect(lambda: self.sendButton.setEnabled(True))
        self.cancel.clicked.connect(self.addUserText.hide)
        self.cancel.clicked.connect(self.user.hide)
        self.cancel.clicked.connect(self.addUserButton.hide)
        self.cancel.clicked.connect(self.addNickButton.show)
        self.cancel.clicked.connect(self.cancel.hide)
        self.cancel.show()

    def appendMessage(self, message, source, show_timestamp_and_nick=True):
        color = self.__getColor(source)

        if show_timestamp_and_nick:
            timestamp = '<font color="' + color + '">(' + getTimestamp() + ') <strong>' + \
                        (self.chat_window.client.nick if source == MSG_SENDER else self.nick) + \
                        ':</strong></font> '
        else:
            timestamp = ''

        # If the user has scrolled up (current value != maximum), do not move the scrollbar
        # to the bottom after appending the message
        shouldScroll = True
        scrollbar = self.chatLog.verticalScrollBar()
        if scrollbar.value() != scrollbar.maximum() and source != constants.SENDER:
            shouldScroll = False

        self.chatLog.append(timestamp + message)

        # Move the vertical scrollbar to the bottom of the chat log
        if shouldScroll:
            scrollbar.setValue(scrollbar.maximum())

    def __linkify(self, text):
        matches = self.urlRegex.findall(text)
        for match in matches:
            text = text.replace(match[0], '<a href="%s">%s</a>' % (match[0], match[0]))
        return text

    def __getColor(self, source):
        if source == MSG_SENDER:
            if qtUtils.is_light_theme:
                return '#0000CC'
            else:
                return '#6666FF'
        elif source == MSG_RECEIVER:
            if qtUtils.is_light_theme:
                return '#CC0000'
            else:
                return '#CC3333'
        else:
            if qtUtils.is_light_theme:
                return '#000000'
            else:
                return '#FFFFFF'

    def disable(self):
        self.disabled = True
        self.chatInput.setReadOnly(True)

    def enable(self):
        self.disabled = False
        self.chatInput.setReadOnly(False)
