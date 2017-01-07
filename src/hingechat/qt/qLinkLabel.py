from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel

class QLinkLabel(QLabel):
    def __init__(self, text, link, parent=None):
        QLabel.__init__(self, parent)

        self.setText("<a href=\"" + link + "\">" + text + "</a>")
        self.setTextFormat(Qt.RichText)
        self.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.setOpenExternalLinks(True)
