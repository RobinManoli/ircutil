import sys
from ircutil.event import Event

class Send():
    def __init__(self, connection):
        self._connection = connection

    def ban(self, chan, mask):
        self.mode( '+b', chan, mask )

    def ctcp(self, chat, command, msg='', reply=False):
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
        Event(self._connection, '>>> ' + data)

    def join(self, channel):
        self.raw('JOIN ' + channel)

    def me(self, chat, msg=''):
        self.ctcp( chat, 'ACTION', msg )

    def msg(self, chat, msg):
        self.raw('PRIVMSG %s :%s' % (chat, msg) )

    def mode(self, mode, chan='', params=''):
        # untested
        if chan:
            self.raw('MODE %s %s %s' % (chan, mode, params))
        else:
            self.raw('MODE %s %s %s' % (self._connection._nick, mode, params))

    def notice(self, chat, msg):
        self.raw('NOTICE %s :%s' % (chat, msg) )

    def nick(self, nick=''):
        self.raw('NICK %s' % str(nick) or 'ircutil')

    def op(self, chan, nick):
        self.mode( '+o', chan, nick )

    def voice(self, chan, nick):
        self.mode( '+v', chan, nick )

    def part(self, channel, msg=''):
        self.raw('PART %s :%s' % (channel, msg))

    def pong(self, pong):
        self.raw('PONG ' + pong)

    def raw(self, data):
        Event(self._connection, '<<< ' + data)
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
        self.raw('TOPIC %s :%s' %(chan, msg))

    def unban(self, chan, mask):
        self.mode( '-b', chan, mask )

    def user(self, ident='ircutil', hostname='ircutil',
             servername='ircutil', realname='ircutil for easy coding irc in python'):
        self.raw('USER %s %s %s :%s' % (ident, hostname, servername, realname))

    def quit(self, msg=''):
        self.raw('QUIT :' + msg)
        
