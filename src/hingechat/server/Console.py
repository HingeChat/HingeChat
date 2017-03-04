import os
import signal

from src.hinge.server.Console import Console
from src.hinge.server import TURNServer


class ServerConsole(Console):

    def __init__(self, nick_map, ip_map):
        Console.__init__(self, nick_map, ip_map)
        
        self.nick_map = TURNServer.nick_map
        self.ip_map = TURNServer.ip_map
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
                if len(cInput) > 0:
                    arg = cInput[1] if len(cInput) == 2 else None
                    self.commands[cInput[0]]['callback'](arg)
            except EOFError:
                self.stop()
            except KeyError:
                print("Unrecognized command")

    def list(self, arg):
        print("Registered nicks\n" + "=" * 16)
        for nick, client in self.nick_map.items():
            print(nick + " - " + str(client.sock))

    def zombies(self, arg):
        print("Zombie Connections\n" + "=" * 18)
        for addr, client in self.ip_map.items():
            print(addr)

    def kick(self, nick):
        if not nick:
            print("Kick command requires a nick")
        else:
            client = self.nick_map.get(nick)
            if client:
                client.kick()
                print("{0} kicked from server".format(nick))
            else:
                print("{0} is not a registered nick".format(nick))

    def kill(self, ip):
        if not ip:
            print("Kill command requires an IP")
        else:
            client = self.ip_map.get(ip)
            if client:
                client.kick()
                print("{0} killed".format(ip))
            else:
                print("{0} is not a zombie".format(ip))

    def stop(self, arg=None):
        os.kill(os.getpid(), signal.SIGINT)

    def help(self, arg):
        help_messages = [cmd[1]['help'] for cmd in iter(self.commands.items())]
        print("Available commands:\n\t{0}".format('\n\t'.join(help_messages)))
