#	Copyright 2016 Robin Manoli - https://github.com/RobinManoli/ircutil
# 
#	This file is part of Ircutil.
#
#	Ircutil is free software: you can redistribute it and/or modify
#	it under the terms of the GNU Lesser General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	Ircutil is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU Lesser General Public License for more details.
#
#	You should have received a copy of the GNU Lesser General Public License
#	along with Ircutil.  If not, see <http://www.gnu.org/licenses/>.

import sys
#from ircutil.event import Event

class Send():
    def __init__(self, connection):
        self._connection = connection

    def action(self, chat, msg=''):
        self.ctcp(chat, 'ACTION', msg)

    def ban(self, chan, mask):
        self.mode( '+b', chan, mask )

    def ctcp(self, chat, command, msg='', reply=False):
        msg = str(msg)
        ctcp = command.upper()
        ctcp += ' ' + msg if msg else ''
        ctcp =chr(1)+ctcp+chr(1)
        if reply:
            return self.notice(chat, ctcp)
        return self.msg(chat, ctcp)

    def deop(self, chan, nick):
        self.mode( '-o', chan, nick )

    def devoice(self, chan, nick):
        self.mode( '-v', chan, nick )

    def echo(self, data):
        #Event(self._connection, '>>> ' + str(data))
        self._connection.eventhandler( '>>> ' + str(data), sendevent=True )

    def join(self, channel, key=''):
        channel = str(channel)
        key = str(key)
        self.raw('JOIN %s %s' %(channel,key))

    def me(self, chat, msg=''):
        self.ctcp( chat, 'ACTION', msg )

    def msg(self, chat, msg):
        chat = str(chat)
        msg = str(msg)
        self.raw('PRIVMSG %s :%s' % (chat, msg) )

    def mode(self, mode, chan='', params=''):
        # untested
        mode = str(mode)
        chan = str(chan)
        params = str(params)
        if chan:
            self.raw('MODE %s %s %s' % (chan, mode, params))
        else:
            self.raw('MODE %s %s %s' % (self._connection._nick, mode, params))

    def notice(self, chat, msg):
        chat = str(chat)
        msg = str(msg)
        self.raw('NOTICE %s :%s' % (chat, msg) )

    def nick(self, nick=''):
        nick = str(nick)
        self.raw('NICK %s' % str(nick) or 'ircutil')

    def op(self, chan, nick):
        self.mode( '+o', chan, nick )

    def password(self, password):
        password = str(password)
        self.raw( 'PASS %s' % str(password) )

    def voice(self, chan, nick):
        self.mode( '+v', chan, nick )

    def part(self, chan, msg=''):
        chan = str(chan)
        msg = str(msg)
        self.raw('PART %s :%s' % (chan, msg))

    def pong(self, pong):
        pong = str(pong)
        self.raw('PONG ' + pong)

    def raw(self, data):
        data = str(data)
        #Event(self._connection, '<<< ' + data)
        self._connection.eventhandler( '<<< ' + data, sendevent=True )
        data = data + '\r\n'
        if sys.version_info > (2,99,99):
            # use byte python 3 and string in python 2
            data = data.encode()
        self._connection._socket.send( data )
        # prevent flood
        # note that this sleeps even on connect, delaying sending USER and NICK before READY
        import time
        time.sleep(1)

    def topic(self, chan, msg=''):
        chan = str(chan)
        msg = str(msg)
        self.raw('TOPIC %s :%s' %(chan, msg))

    def unban(self, chan, mask):
        self.mode( '-b', chan, mask )

    def user(self, ident='ircutil', hostname='ircutil',
             servername='ircutil', realname='ircutil for easy coding irc in python'):
        ident = str(ident)
        hostname = str(hostname)
        servername = str(servername)
        realname = str(realname)
        self.raw('USER %s %s %s :%s' % (ident, hostname, servername, realname))

    def quit(self, msg='', exit=True):
        """
        Send a QUIT command to the IRC server with an optional message.
        If second arg exit is True (as default), the script will terminate.
        """
        msg = str(msg)
        self.raw('QUIT :' + msg)
        if exit:
            import sys
            sys.exit()

