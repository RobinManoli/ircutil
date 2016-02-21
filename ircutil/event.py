"""
IRC REFERENCE
-------------

JOIN
	:nick!~ircDotPy@example.com JOIN #leveluplife
	# on join
	:kornbluth.freenode.net 332 nick #leveluplife :new
	:kornbluth.freenode.net 333 nick #leveluplife nick!~ircDotPy@example.com 1455354288
	:kornbluth.freenode.net 353 nick @ #leveluplife :nick @nick2
	:kornbluth.freenode.net 366 nick #leveluplife :End of /NAMES list.

MODE
	:nick!~ircDotPy@example.com MODE #leveluplife +oo nick nick2
	:nick!~ircDotPy@example.com MODE #leveluplife +p 
	:nick!~ircDotPy@example.com MODE #leveluplife +b *!q@z
	:nick MODE nick :+i


NICK
	:nick!~ircDotPy@example.com NICK :newnick
PRIVMSG
	:nick!~ircDotPy@example.com PRIVMSG #leveluplife :message text
NOTICE
	:nick!~ircDotPy@example.com NOTICE #leveluplife :hi
	:nick!~ircDotPy@example.com NOTICE nick :yo
TOPIC
	:nick!~ircDotPy@example.com TOPIC #leveluplife :topic text
KICK
	:nick!~ircDotPy@example.com KICK #leveluplife nick :kick message

PART
	:nick!~ircDotPy@example.com PART #leveluplife
	:nick!~ircDotPy@example.com PART #leveluplife :"part message"

QUIT
	:nick!~ircDotPy@example.com QUIT :Quit: What's Your Earth Mission?
"""

class Event():
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
        self.addr = addr.lstrip(':')
        if '@' in self.addr:
            # nick!user@example.com
            at_split = self.addr.split('@')
            self.host = at_split[1] if len(at_split) > 1 else ''
            ex_split = at_split[0].split('!')
            self.nick = ex_split[0].lstrip(':')
            self.ident =  ex_split[1] if len(ex_split) > 1 else ''
        else:
            # :server.addr
            self.host = self.addr

    def __init__(self, connection, raw_event):
        # debug
        #print()
        #print(raw_event)
        #print()
        self._connection = connection
        self.send = connection.send
        self.triggers = connection.triggers

        raw_event = raw_event.rstrip('\r') # remove possible \r (in non EFNet)
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
        self.args1 = raw_event.split(' ', 1)[1].lstrip(':') if len(self.split) > 1 else ''
        self.args2 = raw_event.split(' ', 2)[2].lstrip(':') if len(self.split) > 2 else ''
        self.args3 = raw_event.split(' ', 3)[3].lstrip(':') if len(self.split) > 3 else ''
        self.args4 = raw_event.split(' ', 4)[4].lstrip(':') if len(self.split) > 4 else ''
        self.args5 = raw_event.split(' ', 5)[5].lstrip(':') if len(self.split) > 5 else ''

        self.addr = ''
        self.chan = ''
        self.chat = ''
        self.cmd = ''
        self.ctcp = ''
        self.host = ''
        self.ident = ''
        self.mode = ''
        self.nick = ''
        self.newnick = ''
        self.target = ''
        self.type = ''
        self.msg = ''


        if self.arg0 == 'PING':
            self.cmd = 'PING'
            self.type = 'PING'
            self.msg = self.arg1
            self.send.pong( self.msg )

        elif self.arg0 == '<<<':
            self.cmd = self.arg2
            self.type = 'SENT'
            self.msg = self.args1

        elif self.arg0 == '>>>':
            self.cmd = self.arg2
            self.type = 'ECHO'
            self.msg = self.args1

        elif self.arg0 == 'ERROR':
            # untested in this version
            self.cmd = 'ERROR'
            self.type = 'ERROR'
            self.msg = self.args1

        elif self.arg0 == 'NOTICE':
            # untested in this version, but some notices may look like this
            self.cmd = 'NOTICE'
            self.type = 'NOTICE'
            self.msg = self.args1



        elif self.arg1:
            self.cmd = self.arg1
            self.type = self.arg1
            # most common events contain either server addr or nick!ident@host
            self.parse_addr( self.arg0 )

            if self.arg1 == '001':
                # :rajaniemi.freenode.net 001 myBotte :Welcome to the freenode Internet Relay Chat Network myBotte
                self._connection._welcomed = True
                self.type = 'READY'

            if self.arg1 == '005':
                # :rajaniemi.freenode.net 005 myBotte CHANTYPES=# EXCEPTS INVEX CHANMODES=eIbq,k,flj,CFLMPQScgimnprstz CHANLIMIT=#:120 PREFIX=(ov)@+ MAXLIST=bqeI:100 MODES=4 NETWORK=freenode KNOCK STATUSMSG=@+ CALLERID=g :are supported by this server
                for setting in self.args2:
                    if setting[0:10] == 'CHANTYPES=':
                        self._connection._chantypes = setting.split('=')[1]
                

            elif self.arg1 in ('433', '437'):
                # :wolfe.freenode.net 437 * myBot :Nick/channel is temporarily unavailable
                if not self._connection._welcomed:
                    self.renick()


            elif self.arg1 == 'JOIN':
                self.chan = self.arg2.lstrip(':')
                self.chat = self.chan

            elif self.arg1 == 'KICK':
                self.chan = self.arg2
                self.chat = self.chan
                self.msg = self.args4
                self.target = self.arg3


            elif self.cmd == 'MODE':
                # :nick!ident@host MODE nick|chan [+|-A][B][C][-|+D][E][F] [Atarget][Btarget]...
                # :nick!ident@example.com MODE #irc.py +oo nick nick2
                # :nick!ident@example.com MODE #irc.py +p 
                # :nick!identy@example.com MODE #irc.py +b *!b@z
                self.chan = self.arg2
                self.chat = self.chan or self.nick
                self.mode = self.arg3.lstrip(':')
                if len(self.mode) == 2:
                    # only one mode was set this event, so process normally
                    self.target = self.arg4
                    if self.mode == '+o':
                        self.type = 'OP'
                    elif self.mode == '-o':
                        self.type = 'DEOP'
                    elif self.mode == '+v':
                        self.type = 'VOICE'
                    elif self.mode == '-v':
                        self.type = 'DEVOICE'
                    elif self.mode == '+b':
                        self.type = 'BAN'
                    elif self.mode == '-b':
                        self.type = 'UNBAN'
                    
                else:
                    # more than one mode was set this event, so split them all up
                    # and trigger each mode as one event
                    # '+soo nick nick2 becomes ['+s', '+o nick','+o nick2']
                    ntarget = 0
                    sign = ''
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
                            #Event(self._connection, ':%s MODE %s %s%s %s' %(self.addr, self.chan, sign, mode, target))
                            print ( ':%s MODE %s %s%s %s' %(self.addr, self.chan, sign, mode, target) )
                            ntarget += 1
                        else:
                            #Event(self._connection, ':%s MODE %s %s%s' %(self.addr, self.chat, sign, mode))
                            print ( ':%s MODE %s %s%s' %(self.addr, self.chat, sign, mode) )
                    # do not process this multi-mode event any further
                    #return


            elif self.arg1 == 'NICK':
                self.newnick = self.arg2 or 'UNKNOWN'
                if self.nick == self._connection._nick:
                    self._connection._nick = self.newnick
                    # todo: this code worked, but was delayed until next ping:
                    self.send.echo("I'm now known as: " + self._connection._nick)


            elif self.arg1 == 'PART':
                self.chan = self.arg2
                self.chat = self.chan
                self.msg = self.args3


            elif self.arg1 in ('PRIVMSG', 'NOTICE'):
                # chan needs to be string
                self.chan = self.arg2 if self.arg2 and self.arg2[0] in self._connection._chantypes else ''
                self.chat = self.chan or self.nick
                self.msg = self.args3
                if self.msg.startswith( chr(1) ) and self.msg.endswith( chr(1) ):
                    #self.ctcp = self.arg3.upper().lstrip(':').strip( chr(1) ) # depr
                    if self.arg1 == 'PRIVMSG':
                        self.type = 'CTCP'
                        if self.msg == 'VERSION':
                            self.send.ctcp( self.chat, 'VERSION', self._connection._version, reply=True )
                        elif self.msg.startswith('ACTION '):
                            self.type = 'ACTION'
                    else:
                        self.type = 'CTCP_REPLY'


            elif self.arg1 == 'TOPIC':
                self.chan = self.arg2
                self.msg = self.args3


            elif self.arg1 == 'QUIT':
                self.msg = self.args2



        for trigger in self.triggers:
            trigger(self)