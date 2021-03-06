from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QPushButton


class QAcceptDialog(QMessageBox):

    def __init__(self, parent, nick):
        QMessageBox.__init__(self, parent)

        self.accepted = None

        self.setWindowTitle("Accept Connection?")
        self.setText("Received connection from " + nick)
        self.setIcon(QMessageBox.Question)

        self.acceptButton = QPushButton(QIcon.fromTheme('dialog-ok'), "Accept")
        self.rejectButton = QPushButton(QIcon.fromTheme('dialog-cancel'), "Reject")
        self.addButton(self.acceptButton, QMessageBox.YesRole)
        self.addButton(self.rejectButton, QMessageBox.NoRole)

        self.buttonClicked.connect(self.gotAnswer)

    def gotAnswer(self, button):
        if button is self.acceptButton:
            self.accepted = True
        else:
            self.accepted = False

        self.close()

    @staticmethod
    def getAnswer(parent, hostname):
        acceptDialog = QAcceptDialog(parent, hostname)
        acceptDialog.exec_()
        return acceptDialog.accepted
