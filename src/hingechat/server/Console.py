import os
import signal

from src.hinge.server.Console import Console
from src.hinge.server import TURNServer


class ServerConsole(Console):

    def __init__(self, client_manager):
        Console.__init__(self, client_manager)
        self.client_manager = client_manager
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
                command_input = input(">> ").split()
                if len(command_input) > 0:
                    cmd = self.commands[command_input[0]]['callback']
                    if len(command_input) == 2:
                        cmd(command_input[1])
                    else:
                        cmd(None)
                else:
                    pass
            except EOFError:
                self.stop()
            except KeyError:
                print("Unrecognized command")

    def list(self, arg):
        print("Registered nicks\n" + "=" * 16)
        for client in self.client_manager.clients:
            print(client.nick + " - " + str(client.ip))

    def zombies(self, arg):
        print("Zombie Connections\n" + "=" * 18)
        for client in self.client_manager.clients:
            if client.nick is None:
                print(client.ip)
            else:
                pass

    def kick(self, nick):
        if not nick:
            print("Kick command requires a nick")
        else:
            client = self.client_manager.getClientByNick(nick)
            if client:
                client.kick()
                print("{0} kicked from server".format(client.nick))
            else:
                print("{0} is not a registered nick".format(client.nick))

    def kill(self, ip):
        if not ip:
            print("Kill command requires an IP")
        else:
            try:
                clients = self.client_manager.getConnectionsFromIp(ip)
                for client in clients:
                    client.kick()
                print("{0} killed".format(ip))
            except KeyError:
                print("{0} is not a zombie".format(ip))

    def stop(self, arg=None):
        os.kill(os.getpid(), signal.SIGINT)

    def help(self, arg):
        help_messages = [cmd[1]['help'] for cmd in iter(self.commands.items())]
        print("Available commands:\n\t{0}".format('\n\t'.join(help_messages)))
