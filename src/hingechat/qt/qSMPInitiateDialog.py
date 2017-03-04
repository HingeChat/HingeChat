import os
import signal

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout

from src.hingechat.qt.qLine import QLine
from src.hingechat.qt import qtUtils
from src.hinge.utils import *


class QSMPInitiateDialog(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.clickedButton = constants.BUTTON_CANCEL

        # Set the title and icon
        self.setWindowTitle("Authenticate Buddy")
        self.setWindowIcon(QIcon(qtUtils.getAbsoluteImagePath('icon.png')))

        smpQuestionLabel = QLabel("Question:", self)
        self.smpQuestionInput = QLineEdit(self)

        smpAnswerLabel = QLabel("Answer (case sensitive):", self)
        self.smpAnswerInput = QLineEdit(self)

        okayButton = QPushButton(QIcon.fromTheme('dialog-ok'), "OK", self)
        cancelButton = QPushButton(QIcon.fromTheme('dialog-cancel'), "Cancel", self)

        keyIcon = QLabel(self)
        keyIcon.setPixmap(QPixmap(qtUtils.getAbsoluteImagePath('fingerprint.png')).scaledToWidth(50, Qt.SmoothTransformation))

        helpLabel = QLabel("In order to ensure that no one is listening in on your conversation\n"
                           "it's best to verify the identity of your buddy by entering a question\n"
                           "that only your buddy knows the answer to.")

        okayButton.clicked.connect(lambda: self.buttonClicked(constants.BUTTON_OKAY))
        cancelButton.clicked.connect(lambda: self.buttonClicked(constants.BUTTON_CANCEL))

        helpLayout = QHBoxLayout()
        helpLayout.addStretch(1)
        helpLayout.addWidget(keyIcon)
        helpLayout.addSpacing(15)
        helpLayout.addWidget(helpLabel)
        helpLayout.addStretch(1)

        # Float the buttons to the right
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(okayButton)
        buttons.addWidget(cancelButton)

        vbox = QVBoxLayout()
        vbox.addLayout(helpLayout)
        vbox.addWidget(QLine())
        vbox.addWidget(smpQuestionLabel)
        vbox.addWidget(self.smpQuestionInput)
        vbox.addWidget(smpAnswerLabel)
        vbox.addWidget(self.smpAnswerInput)
        vbox.addLayout(buttons)

        self.setLayout(vbox)


    def buttonClicked(self, button):
        self.smpQuestion = self.smpQuestionInput.text()
        self.smpAnswer = self.smpAnswerInput.text()
        self.clickedButton = button
        self.close()


    @staticmethod
    def getQuestionAndAnswer():
        dialog = QSMPInitiateDialog()
        dialog.exec_()
        return dialog.smpQuestion, dialog.smpAnswer, dialog.clickedButton
