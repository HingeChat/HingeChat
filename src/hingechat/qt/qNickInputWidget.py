from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from src.hingechat.qt import qtUtils
from src.hinge.utils import *


class QNickInputWidget(QWidget):

    def __init__(self, image, imageWidth, connect_clicked_slot, nick='', parent=None):
        QWidget.__init__(self, parent)

        self.connect_clicked_slot = connect_clicked_slot
        
        self.image = QLabel(self)
        self.image.setPixmap(QPixmap(qtUtils.getAbsoluteImagePath(image)).scaledToWidth(imageWidth, Qt.SmoothTransformation))

        self.nick_label = QLabel("Nickname:", self)
        self.nick_edit = QLineEdit(nick, self)
        self.nick_edit.setMaxLength(NICK_MAX_LEN)
        self.nick_edit.returnPressed.connect(self.__connectClicked)
        self.nick_edit.setFocus()

        # Connect button
        self.connect_button = QPushButton("Connect", self)
        self.connect_button.resize(self.connect_button.sizeHint())
        self.connect_button.setAutoDefault(False)
        self.connect_button.clicked.connect(self.__connectClicked)

        hbox1 = QHBoxLayout()
        hbox1.addStretch(1)
        hbox1.addWidget(self.nick_label)
        hbox1.addWidget(self.nick_edit)
        hbox1.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox1)
        vbox.addWidget(self.connect_button)
        vbox.addStretch(1)

        hbox2 = QHBoxLayout()
        hbox2.addStretch(1)
        hbox2.addWidget(self.image)
        hbox2.addSpacing(10)
        hbox2.addLayout(vbox)
        hbox2.addStretch(1)

        self.setLayout(hbox2)


    def __connectClicked(self):
        nick = str(self.nick_edit.text()).lower()
        status = isValidNick(nick)
        if status == VALID_NICK:
            self.connect_clicked_slot(nick)
        elif status == INVALID_NICK_CONTENT:
            QMessageBox.warning(self, TITLE_INVALID_NICK, INVALID_NICK_CONTENT)
        elif status == INVALID_NICK_LENGTH:
            QMessageBox.warning(self, TITLE_INVALID_NICK, INVALID_NICK_LENGTH)
        elif status == INVALID_EMPTY_NICK:
            QMessageBox.warning(self, TITLE_EMPTY_NICK, EMPTY_NICK)
