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

# todo, modes +h
class Channel():
    def __init__(self, chan):
        self.chan = chan

        self.ops = []
        self.halfops = []
        self.voices = []
        self.users = []
        self.all = []
        self.topic = ""
        self.topicsetter = ""
        self.topictime = None
        self.modes = ""
        self.k = '' # key
        self.b = [] # bans

    def update_all(self):
        self.all = self.ops[:] + self.halfops[:] + self.voices[:] + self.users[:]
        self.all = list(set( self.all )) # remove duplicates, if certain users have for example both op and voice

    def remove_user( self, nick ):
        if nick in self.ops:
            self.ops.remove(nick)
        elif nick in self.halfops:
            self.halfops.remove(nick)
        elif nick in self.voices:
            self.voices.remove(nick)
        elif nick in self.users:
            self.users.remove(nick)


def update(chans, event):
    if event.QUIT:
        for chan in chans.keys():
            if event.nick in chans[chan].all:
                ch = chans[chan]
                ch.remove_user(event.nick)
                ch.update_all()
        return

    if not event.chan:
        return

    if event.chan.lower() not in chans.keys():
        chans[event.chan.lower()] = Channel(event.chan)

    chan = chans[event.chan.lower()]

    if event.JOIN:
        # do not add self here, because self might be op if channel is empty
        if not event.nick == event._connection._nick:
            chan.users.append(event.nick)

    elif event.PART:
        if event.nick == event._connection._nick:
            del chan
            return
        else:
            chan.remove_user(event.nick)

    elif event.KICK:
        if event.target == event._connection._nick:
            del chan
            return
        else:
            chan.remove_user(event.target)

    elif event.NAMREPLY:
        for nick in event.msg.split():
            if nick[0] == '@':
                if nick.lstrip('@') not in chan.ops:
                    chan.ops.append(nick.lstrip('@'))
            elif nick[0] == '%':
                if nick.lstrip('%') not in chan.halfops:
                    chan.halfops.append(nick.lstrip('%'))
            elif nick[0] == '+':
                if nick.lstrip('+') not in chan.voices:
                    chan.voices.append(nick.lstrip('+'))
            elif nick not in chan.users:
                chan.users.append(nick)

    elif event.MODE and event.target:
        nick = event.target

        if event.mode == '+o':
            # nick may already be opped
            if nick not in chan.ops:
                chan.ops.append( nick )

            # nick may be voiced/opped
            if nick in chan.users:
                chan.users.remove(nick)

        elif event.mode == '+v':
            # nick may already be voiced
            if nick not in chan.voices:
                chan.voices.append( nick )

            # nick may be voiced/opped
            if nick in chan.users:
                chan.users.remove(nick)

        elif event.mode == '-o':
            # nick may already be deopped
            if nick in chan.ops:
                chan.ops.remove( nick )

            # nick may be already deopped or voiced
            if nick not in chan.users and nick not in chan.voices:
                chan.users.append(nick)

        elif event.mode == '-v':
            # nick may already be devoiced
            if nick in chan.voices:
                chan.voices.remove( nick )

            # nick may be already devoiced or opped
            if nick not in chan.users and nick not in chan.ops:
                chan.users.append(nick)

        elif event.mode == '+k':
            chan.k = event.target

        elif event.mode == '-k':
            chan.k = ''

        elif event.mode[0] == '+':
            # modes that add to lists, such as b, E, I
            mode = event.mode[1]
            if not hasattr(chan, mode):
                setattr(chan, mode, [])
            getattr(chan, mode).append(event.target)

        elif event.mode[0] == '-':
            # modes that add to lists, such as b, E, I
            mode = event.mode[1]
            if not hasattr(chan, mode):
                setattr(chan, mode, [])
            else:
                lst = getattr(chan, mode)
                if event.target in lst:
                    lst.remove(event.target)

    elif event.MODE:
        # chan flag modes
        mode = event.mode[1] if len(event.mode) > 1 else ''
        if event.mode and event.mode[0] == '+':
            chan.modes += mode
        elif event.mode:
            chan.modes = chan.modes.replace(mode, '')

    elif event.type == '324':
        # mode #chan
        if event.msg:
            chan.modes = event.msg.lstrip('+')

    elif event.type == '332':
        chan.topic = event.msg

    elif event.type == '333':
        chan.topicsetter = event.arg4
        chan.topictime = int(event.arg5) if event.arg5.isdigit() else event.arg5

    elif event.TOPIC:
        chan.topic = event.msg
        chan.topicsetter = event.addr
        import time
        chan.topictime = time.time()


    chan.update_all()            

