from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal

from src.hinge.utils import *


class QtServerConnectThread(QThread):
    
    success_signal = pyqtSignal()
    failure_signal = pyqtSignal(str)

    def __init__(self, client, success_slot, failure_slot):
        QThread.__init__(self)
        self.client = client
        self.success_signal.connect(success_slot)
        self.failure_signal.connect(failure_slot)

    def run(self):
        try:
            self.client.connectToServer()
            self.success_signal.emit()
        except GenericError as ge:
            self.failure_signal.emit(str(ge))
        except NetworkError as ne:
            self.failure_signal.emit(str(ne))
