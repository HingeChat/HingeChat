import sys
import signal
import argparse

from src.hingechat.qt.qt import QtUI

from src.hinge.server.TURNServer import TURNServer
from src.hingechat.server.Console import ServerConsole
from src.hinge.utils import *


def port_in_range(port):
    if (port < 1) or (port > 65536):
        return False
    else:
        return True


class Main(object):

    def __init__(self, args):
        self.args = args
        if not port_in_range(self.args.port):
            self.error(1)

    def start(self):
        # Overwrite in subclass
        pass

    def stop(self):
        # Overwrite in subclass
        pass

    def error(self, code):
        print(ERROR_CODES[code])
        self.exit()

    def exit(self):
        sys.exit()

    @staticmethod
    def parse_args():
        ap = argparse.ArgumentParser()
        ap.add_argument('-k', '--nick',
                        dest='nick',
                        nargs='?',
                        type=str,
                        help="Nickname to use.")
        ap.add_argument('-r', '--relay',
                        dest='turn',
                        nargs='?',
                        type=str,
                        default=str(DEFAULT_TURN_SERVER),
                        help="The relay server to use.")
        ap.add_argument('-p', '--port',
                        dest='port',
                        nargs='?',
                        type=int,
                        default=str(DEFAULT_PORT),
                        help="Port to listen on (server) or connect to (client).")
        ap.add_argument('-s', '--server',
                        dest='server',
                        default=False,
                        action='store_true',
                        help="Run as TURN server for other clients.")
        return ap.parse_args()


class Client(Main):

    def __init__(self, args):
        Main.__init__(self, args)
        self.qt_interface = QtUI(sys.argv,
                                 self.args.nick,
                                 self.args.turn,
                                 self.args.port)

    def start(self):
        signal.signal(signal.SIGINT, self.stop)
        self.qt_interface.start()

    def stop(self, signal, frame):
        self.qt_interface.stop()
        self.exit()


class Server(Main):

    def __init__(self, args):
        Main.__init__(self, args)
        self.server = TURNServer(self.args.port)
        self.console = ServerConsole(self.server.client_manager)

    def start(self):
        signal.signal(signal.SIGINT, self.stop)
        self.console.start()
        self.server.start()

    def stop(self, signal, frame):
        self.server.stop()
        self.exit()


if __name__ == "__main__":
    args = Main.parse_args()
    if args.server:
        Server(args).start()
    else:
        Client(args).start()
