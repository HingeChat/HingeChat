from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets  import QDialog
from PyQt5.QtWidgets  import QFrame
from PyQt5.QtWidgets  import QHBoxLayout
from PyQt5.QtWidgets  import QLabel
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets  import QVBoxLayout

from . import qtUtils
from .qLine import QLine

from src.hinge.utils import constants


class QWaitingDialog(QDialog):
    def __init__(self, parent, text=""):
        QDialog.__init__(self, parent)

        # Create waiting image
        waitingImage = QMovie(qtUtils.getAbsoluteImagePath('waiting.gif'))
        waitingImage.start()
        waitingImageLabel = QLabel(self)
        waitingImageLabel.setMovie(waitingImage)

        waitingLabel = QLabel(text, self)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(waitingImageLabel)
        hbox.addSpacing(10)
        hbox.addWidget(waitingLabel)
        hbox.addStretch(1)

        self.setLayout(hbox)
