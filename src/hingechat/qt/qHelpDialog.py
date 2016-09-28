from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QVBoxLayout

from qLinkLabel import QLinkLabel

class QHelpDialog(QMessageBox):
    def __init__(self, parent=None):
        QMessageBox.__init__(self, parent)

        self.setWindowTitle("Help")

        helpText = QLabel("Coming soon.", self)

        self.setIcon(QMessageBox.Question)
        self.setStandardButtons(QMessageBox.Ok)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(helpText)
        vbox.addStretch(1)

        # Replace the default label with our own custom layout
        layout = self.layout()
        layout.addLayout(vbox, 0, 1)
