from src.hinge.server.Console import Console
from src.hinge.server import TURNServer

class ServerConsole(Console):
    def __init__(self, nickMap, ipMap):
        Console.__init__(self, nickMap, ipMap)
        self.nickMap = TURNServer.nickMap
        self.ipMap = TURNServer.ipMap

        self.commands = {
            'list': {
                'callback': self.list,
                'help': 'list\t\tlist active connections'
            },
            'zombies': {
                'callback': self.zombies,
                'help': 'zombies\t\tlist zombie connections'
            },
            'kick': {
                'callback': self.kick,
                'help': 'kick [nick]\tkick the given nick from the server'
            },
            'kill': {
                'callback': self.kill,
                'help': 'kill [ip]\tkill the zombie with the given IP'
            },
            'stop': {
                'callback': self.stop,
                'help': 'stop\t\tstop the server'
            },
            'help': {
                'callback': self.help,
                'help': 'help\t\tdisplay this message'
            },
        }

    def run(self):
        while True:
            try:
                cInput = input(">> ").split()

                if len(cInput) == 0:
                    continue

                command = cInput[0]
                arg = cInput[1] if len(cInput) == 2 else None

                self.commands[command]['callback'](arg)
            except EOFError:
                self.stop()
            except KeyError:
                print("Unrecognized command")

    def list(self, arg):
        print("Registered nicks")
        print("================")

        for nick, client in self.nickMap.items():
            print(nick + " - " + str(client.sock))

    def zombies(self, arg):
        print("Zombie Connections")
        print("==================")

        for addr, client in self.ipMap.items():
            print(addr)

    def kick(self, nick):
        if not nick:
            print("Kick command requires a nick")
            return

        try:
            client = self.nickMap[nick]
            client.kick()
            print("%s kicked from server" % nick)
        except KeyError:
            print("%s is not a registered nick" % nick)

    def kill(self, ip):
        if not ip:
            print("Kill command requires an IP")
            return

        try:
            client = self.ipMap[ip]
            client.kick()
            print("%s killed" % ip)
        except KeyError:
            print("%s is not a zombie" % ip)

    def stop(self, arg=None):
        os.kill(os.getpid(), signal.SIGINT)

    def help(self, arg):
        delimeter = '\n\t'
        helpMessages = [__command[1]['help'] for __command in iter(self.commands.items())]
        print("Available commands:%s%s" % (delimeter, delimeter.join(helpMessages)))