import sys
import socket
from irc.send import Send
from irc.event import Event


class Connection():
    def __init__(self):
        self.nick = "ircDotPy" # main nick
        self._nick = self.nick # current nick
        self.ident = "ircDotPy"
        self.realname = "irc.py for coding irc in python"
        self.server = "irc.freenode.net" # main server
        self._server = '' # current server
        #self.__server = '' # last server # not used until mature decision
        self.ipv6 = False

        self.nicks = [] # list of alternative nicks
        self.servers = [] # list of alternative servers with optional ports

        self.triggers = [] # list of functions to run on each irc event
        self._connected = False
        self._welcomed = False # when accepted on server (for nick loop)
        self._chantypes = '#'

        self._buffer = ''
        self._socket = None
        self.send = Send(self)

        self.ban = self.send.ban
        self.ctcp = self.send.ctcp
        self.deop = self.send.deop
        self.devoice = self.send.devoice
        self.echo = self.send.echo
        self.join = self.send.join
        self.me = self.send.me
        self.msg = self.send.msg
        self.mode = self.send.mode
        self.notice = self.send.notice
        self.op = self.send.op
        self.part = self.send.part
        self.voice = self.send.voice
        self.raw = self.send.raw
        self.topic = self.send.topic
        self.unban = self.send.unban
        self.quit = self.send.quit

        self.hostname = 'ircDotPy' # relevant for irc-servers, not clients
        self.servername = 'ircDotPy' # relevant for irc-servers, not clients
        self._version = "irc.py 1.0"

    def _loop(self):
        while True:
            newdata = self._socket.recv(4096)
            if sys.version_info > (2,99,99):
                # use byte python 3 and string in python 2
                newdata = newdata.decode()
            newdata = self._buffer + newdata

            if not newdata:
                break

            # split events by \n as EFNet doesn't include \r
            events = newdata.split('\n')
            # if received events are complete the last list item is an empty string
            # otherwise the last list item is an incomplete irc event
            self._buffer = events.pop()

            for event in events:
                Event(self, event)

    def connect(self, server=''):
        """
        Connect to IRC.
        Use the server (optionally trailed with :port) parameter
        to create your own connection loop.
        Otherwise the reconnection happens automatically when lost,
        using Connection.server
        """
        def do_connect(server):
            import sys
            self.echo( 'Running Python ' + str(sys.version) )

            server_split = server.split(':')
            server = server_split[0]
            port = server_split[1] if len(server_split) > 1 else '6667'
            port = int(port) if port.isdigit() else 6667

            self._socket = socket.socket(socket.AF_INET6 if self.ipv6 else socket.AF_INET, socket.SOCK_STREAM)
            self.echo('Connecting to %s:%d...' % (server, port))
            try:
                self._socket.connect(( server, port ))
                self.echo('Connected!')
                self._connected = True
    
                self._nick = self.nick
                self.send.nick( self.nick )
                self.send.user(self.ident, self.hostname, self.servername, self.realname)
                self._loop()
            except Exception as e:
                #print( str(e) )
                import sys
                import traceback
                import os
                ex_type, ex, tb = sys.exc_info()
                traceback.print_tb(tb)
                self.echo('DISCONNECTED - ' + str(ex))
                print ()

            self._connected = False
            self._welcomed = False
            self._socket.close()

        if server:
            print( 'Connect without loop...' )
            do_connect(server)

        else:
            self._server = self.server
            server = self.server
            while True:
                # connect-loop
                do_connect( server )
                # connection lost
                server = self._server # server which lost connection
                if not self.servers or server == self.servers[-1]:
                    # restart from primary server
                    server = self.server
                elif server == self.server and self.servers:
                    # use first alternative server
                    server = self.servers[0]
                elif server in self.servers:
                    index = self.servers.index(server)
                    server = self.servers[index + 1]
                self._server = server

