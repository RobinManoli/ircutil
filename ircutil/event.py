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

from __future__ import print_function
import ircutil.channel
from datetime import datetime

class Event():
    def __init__(self, connection):
        self._connection = connection
        self.send = connection.send
        self.triggers = connection.triggers

    def renick(self):
        nick = self._connection._nick
        if not self._connection.nicks or nick == self._connection.nicks[-1] \
           or (nick not in self._connection.nicks and nick != self._connection.nick):
            nick = nick + '_'
        elif nick == self._connection.nick and self._connection.nicks:
            nick = self._connection.nicks[0]
        elif nick in self._connection.nicks and nick != self._connection.nicks[-1]:
            index = self._connection.nicks.index(nick)
            nick = self._connection.nicks[index + 1]
        self._connection._nick = nick
        self.send.nick(nick)

    def parse_addr( self, addr ):
        self.addr = addr[1:] if addr and addr[0] == ':' else addr
        if '@' in self.addr:
            # nick!user@example.com
            at_split = self.addr.split('@')
            self.host = at_split[1] if len(at_split) > 1 else ''
            ex_split = at_split[0].split('!')
            self.nick = ex_split[0]#.lstrip(':') # don't use lstrip
            self.ident =  ex_split[1] if len(ex_split) > 1 else ''
        else:
            # :server.addr
            self.host = self.addr

    def raw_output(self):
        now = datetime.now() #.strftime('%H:%M:%S')

        if self.MOTD and not self._connection.raw_output_display_motd:
            return

        def output(func_or_true, color=''):
            try:
                print(func_or_true(self))
            except TypeError:
                # not callable
                end = ' ' if self.PING else '\n'
                if color:
                    print(ircutil.colors.BLUE + now.strftime('%H:%M:%S'), self._connection._server, color + self.raw + ircutil.colors.WHITE, end=end)
                else:
                    print(now.strftime('%H:%M:%S'), self._connection._server, '->', self.raw, end=end)

        if self._connection.raw_colored_output is not None:
            import ircutil.colors
            if self.SENT:
                # command was sent, not received
                color = ircutil.colors.VIOLET
            elif self.ERROR or self.KICK:
                color = ircutil.colors.RED
            elif self.NOTICE or self.MSG:
                color = ircutil.colors.YELLOW
            elif self.arg1 in ('JOIN', 'PART', 'QUIT'):
                color = ircutil.colors.BLUE2
            elif self.arg1 in ('MODE', 'NICK', 'TOPIC'):
                color = ircutil.colors.GREEN
            else:
                color = ircutil.colors.GREY
            output(self._connection.raw_colored_output, color)

        elif self._connection.raw_output is not None:
            output(self._connection.raw_output)


    def handle(self, raw_event):
        self.parse(raw_event)
        self.raw_output() # output raw first, so it will not be written after .send() responses

        if self.PING:
            self.send.pong( self.msg )

        elif self.WELCOME and self._connection.autojoin and isinstance(self._connection.autojoin, list):
            for chan in self._connection.autojoin:
                self.send.join(chan)

        elif self.NICK:
            # todo: this code worked, but was delayed until next ping:
            self.send.echo("I'm now known as: " + self._connection._nick)

        elif self.CTCP and self.ctcp == 'VERSION':
            self.send.ctcp( self.chat, 'VERSION', self._connection._version, reply=True )

        elif self.arg1 in ('433', '437'):
            # :wolfe.freenode.net 437 * myBot :Nick/channel is temporarily unavailable
            if not self._connection._welcomed:
                self.renick()

        for trigger in self.triggers:
            trigger(self)


    def parse(self, raw_event):
        # debug
        #import inspect
        #print( 'raw event caller name:', inspect.stack()[1][3], raw_event)
        #rw = event.raw.encode('string_escape') # repr(event.raw)

        #raw_event = raw_event.rstrip('\r') # remove possible \r (in non EFNet)
        # clean event data (if it comes from echo it might contains new lines, and also if it's non efnet it contains them)

        # https://tools.ietf.org/html/rfc2812 for more
        self.ACTION = False
        self.BAN = False
        # self.CONNECTED = False # connected to socket, but not ready to chat, not implemented yet
        self.CTCP = False
        self.CTCP_REPLY = False
        self.DEOP = False
        self.DEVOICE = False
        self.DEHALFOP = False
        # self.DISCONNECTED = False # disconnected from socket, not implemented yet
        self.ECHO = False
        self.ERROR = False
        self.HALFOP = False
        self.JOIN = False
        self.KICK = False
        self.MODE = False
        self.MOTD = False
        self.MSG = False
        self.NAMREPLY = False
        self.NICK = False
        self.NOTICE = False
        self.OP = False
        self.PART = False
        self.PING = False
        self.PRIVMSG = False
        self.QUIT = False
        self.SENT = False
        self.TOPIC = False
        self.UNBAN = False
        self.VOICE = False
        self.WELCOME = False

        raw_event = raw_event.replace('\r', '').replace('\n', '')
        self.raw = raw_event
        self.split = raw_event.split()
        if not self.split:
            return

        self.arg0 = self.split[0]
        self.arg1 = self.split[1] if len(self.split) > 1 else ''
        self.arg2 = self.split[2] if len(self.split) > 2 else ''
        self.arg3 = self.split[3] if len(self.split) > 3 else ''
        self.arg4 = self.split[4] if len(self.split) > 4 else ''
        self.arg5 = self.split[5] if len(self.split) > 5 else ''
        self.arg6 = self.split[6] if len(self.split) > 6 else ''
        self.arg7 = self.split[7] if len(self.split) > 7 else ''

        # get full string of event starting from argX
        self.args1 = raw_event.split(' ', 1)[1] if len(self.split) > 1 else ''
        self.args2 = raw_event.split(' ', 2)[2] if len(self.split) > 2 else ''
        self.args3 = raw_event.split(' ', 3)[3] if len(self.split) > 3 else ''
        self.args4 = raw_event.split(' ', 4)[4] if len(self.split) > 4 else ''
        self.args5 = raw_event.split(' ', 5)[5] if len(self.split) > 5 else ''

        self.args1 = self.args1[1:] if self.args1 and self.args1[0] == ':' else self.args1
        self.args2 = self.args2[1:] if self.args2 and self.args2[0] == ':' else self.args2
        self.args3 = self.args3[1:] if self.args3 and self.args3[0] == ':' else self.args3
        self.args4 = self.args4[1:] if self.args4 and self.args4[0] == ':' else self.args4
        self.args5 = self.args5[1:] if self.args5 and self.args5[0] == ':' else self.args5

        self.addr = ''
        self.chan = ''
        self.chat = ''
        self.ctcp = ''
        self.host = ''
        self.ident = ''
        self.mode = ''
        self.nick = ''
        #self.newnick = '' # replaced by self.target
        self.target = ''
        self.type = ''
        self.msg = ''

        if self.arg0 == 'PING':
            self.type = 'PING'
            self.msg = self.arg1
            self.PING = True

        elif self.arg0 == '<<<':
            self.type = self.arg0
            self.msg = self.args1
            self.SENT = True

        elif self.arg0 == '>>>':
            self.type = self.arg0
            self.msg = self.args1
            self.ECHO = True

        elif self.arg0 == 'ERROR':
            # untested in this version
            self.type = 'ERROR'
            self.msg = self.args1
            self.ERROR = True

        elif self.arg0 == 'NOTICE':
            # untested in this version, but some notices may look like this
            self.type = 'NOTICE'
            self.msg = self.args1
            self.NOTICE = True


        elif self.arg1:
            self.type = self.arg1
            # most common events contain either server addr or nick!ident@host
            self.parse_addr( self.arg0 )

            if self.arg1 == '001':
                # :rajaniemi.freenode.net 001 myBotte :Welcome to the freenode Internet Relay Chat Network myBotte
                self._connection._welcomed = True
                self.WELCOME = True

            if self.arg1 == '005':
                # :rajaniemi.freenode.net 005 myBotte CHANTYPES=# EXCEPTS INVEX CHANMODES=eIbq,k,flj,CFLMPQScgimnprstz CHANLIMIT=#:120 PREFIX=(ov)@+ MAXLIST=bqeI:100 MODES=4 NETWORK=freenode KNOCK STATUSMSG=@+ CALLERID=g :are supported by this server
                for setting in self.args2:
                    if setting[0:10] == 'CHANTYPES=':
                        self._connection._chantypes = setting.split('=')[1]


            elif self.arg1 == '324':
                # reply to: MODE #mychan
                # :sinisalo.freenode.net 324 mynick #mychan +ps
                self.chan = self.arg3
                self.chat = self.chan
                self.msg = self.args4


            elif self.arg1 == '332':
                self.chan = self.arg3
                self.chat = self.chan
                self.msg = self.args4


            elif self.arg1 == '333':
                self.chan = self.arg3
                self.chat = self.chan
                self.msg = self.args4


            elif self.arg1 == '353':
                # namreply
                # :irc.portlane.se 353 mynick = #chan :mynick +nick2 @nick3
                self.NAMREPLY = True
                self.chan = self.arg4
                self.chat = self.chan
                self.msg = self.args5

            elif self.arg1 == '372':
                # namreply
                self.MOTD = True

            elif self.arg1 == 'JOIN':
                self.chan = self.arg2[1:] if self.arg2 and self.arg2[0] == ':' else self.arg2
                self.chat = self.chan
                self.JOIN = True


            elif self.arg1 == 'KICK':
                self.chan = self.arg2
                self.chat = self.chan
                self.msg = self.args4
                self.target = self.arg3
                self.KICK = True


            elif self.arg1 == 'MODE':
                # :nick!ident@host MODE nick|chan [+|-A][B][C][-|+D][E][F] [Atarget][Btarget]...
                # :nick!ident@example.com MODE #ircutil +oo nick nick2
                # :nick!ident@example.com MODE #ircutil +p 
                # :nick!identy@example.com MODE #ircutil +b *!b@z
                # :ezBot_ MODE ezBot_ :i
                self.MODE = True
                self.chan = self.arg2 if self.arg2 and self.arg2[0] in self._connection._chantypes else ''
                self.chat = self.chan or self.nick
                self.mode = self.arg3 if self.arg3 and self.arg3[0] == ':' else self.arg3
                if len(self.mode) < 3 or not self.chan:
                    # only one or less mode was set this event, or it was not a channel mode, so process normally
                    self.target = self.arg4
                    if self.mode == '+o':
                        self.OP = True
                    elif self.mode == '-o':
                        self.DEOP = True
                    elif self.mode == '+v':
                        self.VOICE = True
                    elif self.mode == '-v':
                        self.DEVOICE = True
                    elif self.mode == '+b':
                        self.BAN = True
                    elif self.mode == '-b':
                        self.UNBAN = True
                    elif self.mode == '+h':
                        self.HALFOP = True
                    elif self.mode == '-h':
                        self.DEHALFOP = True

                else:
                    # more than one mode was set this event, so split them all up
                    # and trigger each mode as one event
                    # '+soo nick nick2 becomes ['+s', '+o nick','+o nick2']
                    ntarget = 0
                    sign = ''
                    modes = []
                    for char in self.mode:  
                        if char == '+' or char == '-':
                            # remember if last sign was + or -
                            sign = char
                            continue
                        else:
                            mode = char
                        # check if channel mode is one that uses target, and that target exists
                        if self.chan and mode in 'bvoIelk' and len(self.split) > ntarget + 4:
                            target = self.split[4+ntarget]
                            raw = ':%s MODE %s %s%s %s' %(self.addr, self.chan, sign, mode, target)
                            modes.append(raw)
                            #print(raw)
                            #Event(self._connection, ':%s MODE %s %s%s %s' %(self.addr, self.chan, sign, mode, target)) # old event handler
                            ntarget += 1
                        else:
                            raw = ':%s MODE %s %s%s' %(self.addr, self.chat, sign, mode)
                            modes.append(raw)
                            #print(raw)
                            #Event(self._connection, ':%s MODE %s %s%s' %(self.addr, self.chat, sign, mode)) # old event handler

                    # process all multimodes before handling
                    for mode in modes:
                        #print('parsed multimode:', mode) # debug
                        self.handle(mode)
                    # do not process this multi-mode event any further
                    return


            elif self.arg1 == 'NICK':
                self.target = self.arg2 or 'UNKNOWN'
                self.target = self.target[1:] if self.target and self.target[0] == ':' else self.target
                if self.nick == self._connection._nick:
                    self._connection._nick = self.target
                self.NICK = True


            elif self.arg1 == 'PART':
                self.chan = self.arg2
                self.chat = self.chan
                self.msg = self.args3
                self.PART = True


            elif self.arg1 in ('PRIVMSG', 'NOTICE'):
                # chan needs to be string
                self.chan = self.arg2 if self.arg2 and self.arg2[0] in self._connection._chantypes else ''
                self.chat = self.chan or self.nick
                self.msg = self.args3
                self.MSG = True if self.arg1 == 'PRIVMSG' else False
                self.NOTICE = not self.MSG
                if self.msg.startswith( chr(1) ) and self.msg.endswith( chr(1) ):
                    self.msg = self.msg[1:-1] # remove chr(1)
                    self.ctcp = self.msg.upper().split(' ', 1)[0]
                    self.msg = self.msg[ len(self.ctcp) + 1: ] # remove self.ctcp + one space from self.msg
                    #self.msg = self.msg[1:] if self.msg and self.msg[0] == ':' else self.msg # seems like colon is outside chr(1)
                    if self.arg1 == 'PRIVMSG':
                        self.CTCP = True
                        if self.ctcp == "ACTION":
                            self.ACTION = True
                    else:
                        self.CTCP_REPLY = True


            elif self.arg1 == 'TOPIC':
                self.chan = self.arg2
                self.msg = self.args3
                self.TOPIC = True


            elif self.arg1 == 'QUIT':
                self.msg = self.args2
                self.QUIT = True

        if hasattr(self, self.type):
            setattr(self, self.type, True)
        ircutil.channel.update( self._connection.chans, self )


"""
IRC REFERENCE
-------------

JOIN
	:nick!~ircutil@example.com JOIN #leveluplife
	# on join
	:kornbluth.freenode.net 332 nick #leveluplife :new
	:kornbluth.freenode.net 333 nick #leveluplife nick!~ircutil@example.com 1455354288
	:kornbluth.freenode.net 353 nick @ #leveluplife :nick @nick2
	:kornbluth.freenode.net 366 nick #leveluplife :End of /NAMES list.

MODE
	:nick!~ircutil@example.com MODE #leveluplife +oo nick nick2
	:nick!~ircutil@example.com MODE #leveluplife +p 
	:nick!~ircutil@example.com MODE #leveluplife +b *!q@z
	:nick MODE nick :+i


NICK
	:nick!~ircutil@example.com NICK :newnick
PRIVMSG
	:nick!~ircutil@example.com PRIVMSG #leveluplife :message text
NOTICE
	:nick!~ircutil@example.com NOTICE #leveluplife :hi
	:nick!~ircutil@example.com NOTICE nick :yo
TOPIC
	:nick!~ircutil@example.com TOPIC #leveluplife :topic text
KICK
	:nick!~ircutil@example.com KICK #leveluplife nick :kick message

PART
	:nick!~ircutil@example.com PART #leveluplife
	:nick!~ircutil@example.com PART #leveluplife :"part message"

QUIT
	:nick!~ircutil@example.com QUIT :Quit: What's Your Earth Mission?
"""

