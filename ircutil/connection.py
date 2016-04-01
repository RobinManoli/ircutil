from __future__ import print_function

import sys
import socket
from ircutil.send import Send
#from ircutil.event import Event


class Connection():
    def _eventhandler(self, eventstr, sendevent=False):
        from ircutil.event import Event

        if sendevent:
            # since send events might happen inside normal event function call
            # (pong happens inside ping, and happens on ctcp version, nick collission, etc)
            # use a special event for sending
            if not hasattr(self, '_Sendevent'):
                self._Sendevent = Event(self)
            self._Sendevent.handle(eventstr)

        else:
            #Event(self, eventstr)
            if not hasattr(self, '_Event'):
                self._Event = Event(self)
            self._Event.handle(eventstr)


    def __init__(self):
        self.nick = "ircutil" # main nick
        self._nick = self.nick # current nick
        self.ident = "ircutil"
        self.realname = "ircutil for easy coding irc in python"
        self.server = "irc.freenode.net" # main server
        self._server = '' # current server
        #self.__server = '' # last server # not used until mature decision
        self.ipv6 = False # default setting for servers, can also be added as a server specific arg such as 'irc.freenode.net ipv6'
        self.password = '' # default setting for servers, can also be added as a server specific arg such as 'irc.freenode.net password=mypassword'

        self.nicks = [] # list of alternative nicks
        self.servers = [] # list of alternative servers with optional ports
        self.chans = {} # keeps records of channel users, topics and modes

        self.triggers = [] # list of functions to run on each irc event
        self.eventhandler = self._eventhandler # override this to create custom event handler, that receives sendevent argument from self.send (remember to run self.triggers)
        self._connected = False
        self._emulated = False
        self._welcomed = False # when accepted on server (for nick loop)
        self._chantypes = '#'

        self._buffer = ''
        self._socket = None
        self.send = Send(self)

        self.action = self.send.action
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

        self.hostname = 'ircutil' # relevant for irc-servers, not clients
        self.servername = 'ircutil' # relevant for irc-servers, not clients
        self._version = "python ircutil 0.96 beta"

    def _loop(self):
        while True:
            newdata = self._socket.recv(4096)
            if sys.version_info >= (3,0):
                try:
                    newdata = newdata.decode() # fails on certain Swedish chars in ISO-8859-1
                except UnicodeDecodeError:
                    try:
                        # If you don't know the encoding, then to read binary input into string in Python 3 and Python 2 compatible way, use ancient MS-DOS cp437 encoding:
                        # http://stackoverflow.com/a/27527728/942621
                        newdata = newdata.decode('cp437') # displays the Swedish chars
                        #print('cp437', newdata)
                    except:
                        raise
                        #newdata = str(newdata, 'utf-8', 'ignore') # seems to work but removes the Swedish chars
                        # http://stackoverflow.com/questions/436220/python-is-there-a-way-to-determine-the-encoding-of-text-file
                        #newdata = unicode(newdata, errors='ignore') #python2?
            newdata = self._buffer + newdata

            if not newdata:
                break

            # split events by \n as EFNet doesn't include \r
            events = newdata.split('\n')
            # if received events are complete the last list item is an empty string
            # otherwise the last list item is an incomplete irc event
            self._buffer = events.pop()

            for event in events:
                self.eventhandler(event)
                #Event(self, event)

    def emulate(self, file):
        """
        Emulate a connection by running predefined IRC commands from a text file (first arg).
        """
        self._emulated = True
        self._nick = self.nick

        class FakeSocket():
            def send(self, *args):
                "Creates a fake socket which does nothing instead of sending through socket."

        with open(file) as f:
            for raw_event in f.readlines():
                raw_event = raw_event.strip()
                try:
                    print('Emulating:', raw_event)
                    self._socket = FakeSocket()
                    #event = Event(self, raw_event)
                    self.eventhandler(raw_event)

                except Exception as e:
                    import sys
                    import traceback
                    import os
                    print()
                    ex_type, ex, tb = sys.exc_info()
                    print(ex_type)
                    print(ex)
                    traceback.print_tb(tb)

        self._emulated = False
        self._socket = None
                

    def connect(self, server=''):
        """
        Connect to IRC.
        Use the server (optionally trailed with :port) parameter
        to create your own connection loop.
        Otherwise the reconnection happens automatically when lost,
        using Connection.server

        Arguments may follow after server[:port], separated by spaces,
        for the following server specific settings (which override Connection.setting):
        ipv4, ipv6, password=mypassword

        For example:
        irc.freenode.net ipv6 password=mypassword
        irc.freenode.net password= # do not send default password
        """
        def do_connect(server):
            import sys
            self.echo( 'Running Python ' + str(sys.version) )

            self.chans = {} # clear chans on reconnects
            server_args = server.split()

            server_port = server_args[0].split(':')
            server = server_port[0]
            port = server_port[1] if len(server_port) > 1 else '6667'
            port = int(port) if port.isdigit() else 6667

            ipv4 = True if 'ipv4' in server_args else False
            ipv6 = True if 'ipv6' in server_args else False
            # name variable passwords to indicate that it is a list
            passwords = [arg.split('=',1)[1] for arg in server_args if arg.startswith('password=')]

            self._socket = socket.socket(socket.AF_INET6 if (self.ipv6 and not ipv4) or ipv6 else socket.AF_INET, socket.SOCK_STREAM)
            self.echo('Connecting to %s:%d...' % (server, port))
            try:
                self._socket.connect(( server, port ))
                self.echo('Connected!')
                self._connected = True
    
                self._nick = self.nick
                if passwords and passwords[0]:
                    self.send.password( passwords[0] )
                elif self.password and not passwords:
                    # send default pass if passwords is not explicitly empty
                    self.send.password( self.password )
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
                self.echo( 'DISCONNECTED - %s %s %s' % (str(ex_type),str(ex),str(traceback.extract_stack())) )
                print ()

            self._connected = False
            self._welcomed = False
            self._socket.close()

        if server:
            #print( 'Connect without loop...' )
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

