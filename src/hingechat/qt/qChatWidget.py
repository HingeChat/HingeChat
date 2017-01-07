import re

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QTimer
from PyQt4.QtGui import QFontMetrics
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QSplitter
from PyQt4.QtGui import QTextBrowser
from PyQt4.QtGui import QTextEdit
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QWidget

import qtUtils

from src.hinge.utils import constants
from src.hinge.utils import utils
from src.hinge.utils import errors

class QChatWidget(QWidget):
    def __init__(self, connectionManager, nick, parent=None):
        QWidget.__init__(self, parent)

        self.connectionManager = connectionManager
        self.nick = nick
        self.isDisabled = False
        self.wasCleared = False

        self.urlRegex = re.compile(constants.URL_REGEX)

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

    def chatInputTextChanged(self):
        # Check if the text changed was the text box being cleared to avoid sending an invalid typing status
        if self.wasCleared:
            self.wasCleared = False
            return

        if str(self.chatInput.toPlainText())[-1:] == '\n':
            self.sendMessage()
        else:
            # Start a timer to check for the user stopping typing
            self.typingTimer.start(constants.TYPING_TIMEOUT)
            self.sendTypingStatus(constants.TYPING_START)

    def stoppedTyping(self):
        self.typingTimer.stop()
        if str(self.chatInput.toPlainText()) == '':
            self.sendTypingStatus(constants.TYPING_STOP_WITHOUT_TEXT)
        else:
            self.sendTypingStatus(constants.TYPING_STOP_WITH_TEXT)

    def sendMessage(self):
        if self.isDisabled:
            return

        self.typingTimer.stop()

        text = str(self.chatInput.toPlainText())[:-1]

        # Don't send empty messages
        if text == '':
            return

        # Convert URLs into clickable links
        text = self.__linkify(text)

        # Add the message to the message queue to be sent
        self.connectionManager.getClient(self.otherNick).sendChatMessage(text)

        # Clear the chat input
        self.wasCleared = True
        self.chatInput.clear()

        self.appendMessage(text, constants.SENDER)

    def sendTypingStatus(self, status):
        self.connectionManager.getClient(self.otherNick).sendTypingMessage(status)

    def showNowChattingMessage(self, nick):
        self.otherNick = nick
        self.appendMessage("You are now securely chatting with " + self.otherNick + " :)",
                           constants.SERVICE, showTimestampAndNick=False)

        self.appendMessage("It's a good idea to verify the communcation is secure by selecting "
                           "\"authenticate buddy\" in the options menu.", constants.SERVICE, showTimestampAndNick=False)

        self.addNickButton = QPushButton('Add', self)
        self.addNickButton.setGeometry(584, 8, 31, 23)
        self.addNickButton.clicked.connect(self.addNickScreen)
        self.addNickButton.show()

    def addUser(self, user):
        nick = str(user.text()).lower()

        # Validate the given nick
        nickStatus = utils.isValidNick(nick)
        if nickStatus == errors.VALID_NICK:
            nicks = [nick, self.otherNick]
            self.connectionManager.openGroupChat(self.nick, nicks)
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

    def appendMessage(self, message, source, showTimestampAndNick=True):
        color = self.__getColor(source)

        if showTimestampAndNick:
            timestamp = '<font color="' + color + '">(' + utils.getTimestamp() + ') <strong>' + \
                        (self.connectionManager.nick if source == constants.SENDER else self.otherNick) + \
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
        if source == constants.SENDER:
            if qtUtils.isLightTheme:
                return '#0000CC'
            else:
                return '#6666FF'
        elif source == constants.RECEIVER:
            if qtUtils.isLightTheme:
                return '#CC0000'
            else:
                return '#CC3333'
        else:
            if qtUtils.isLightTheme:
                return '#000000'
            else:
                return '#FFFFFF'


    def disable(self):
        self.isDisabled = True
        self.chatInput.setReadOnly(True)


    def enable(self):
        self.isDisabled = False
        self.chatInput.setReadOnly(False)
