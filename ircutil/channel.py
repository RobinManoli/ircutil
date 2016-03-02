# todo, modes +ovh, kicks
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
        #self.modes = "" # not implemented
        #self.key
        #self.bans

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
    if event.type == 'QUIT':
        for chan in chans.keys():
            if event.nick in chans[chan].all:
                ch = chans[chan]
                ch.remove_user(event.nick)
                ch.update_all()
        return

    if event.chan.lower() not in chans.keys():
        chans[event.chan.lower()] = Channel(event.chan)

    chan = chans[event.chan.lower()]

    if event.type == 'JOIN':
        # do not add self here, because self might be op if channel is empty
        if not event.nick == event._connection._nick:
            chan.users.append(event.nick)

    elif event.type == 'PART':
        if event.nick == event._connection._nick:
            del chan
            return
        else:
            chan.remove_user(event.nick)

    elif event.type == 'KICK':
        if event.target == event._connection._nick:
            del chan
            return
        else:
            chan.remove_user(event.target)

    elif event.type == 'NAMEREPLY':
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

    elif event.cmd == 'MODE' and event.target:
        nick = event.target

        if event.mode == '+o':
            # nick may already be opped
            if nick not in chan.ops:
                chan.ops.append( nick )

            # nick may be voiced/opped
            if nick in chan.users:
                chan.users.remove(nick)

        if event.mode == '+v':
            # nick may already be voiced
            if nick not in chan.voices:
                chan.voices.append( nick )

            # nick may be voiced/opped
            if nick in chan.users:
                chan.users.remove(nick)

        if event.mode == '-o':
            # nick may already be deopped
            if nick in chan.ops:
                chan.ops.remove( nick )

            # nick may be already deopped or voiced
            if nick not in chan.users and nick not in chan.voices:
                chan.users.append(nick)

        if event.mode == '-v':
            # nick may already be devoiced
            if nick in chan.voices:
                chan.voices.remove( nick )

            # nick may be already devoiced or opped
            if nick not in chan.users and nick not in chan.ops:
                chan.users.append(nick)


    elif event.cmd == '332':
        chan.topic = event.msg

    elif event.cmd == '333':
        chan.topicsetter = event.arg4
        chan.topictime = int(event.arg5) if event.arg5.isdigit() else event.arg5

    elif event.type == 'TOPIC':
        chan.topic = event.msg
        chan.topicsetter = event.addr
        import time
        chan.topictime = time.time()


    chan.update_all()            
    

"""
[1456249763] :nick!~user@ip JOIN :#philosophy
[1456249763] :irc.portlane.se 332 gak #philosophy :topic ...
[1456249763] :irc.portlane.se 333 gak #philosophy nik!usr@ip 1454850268
[1456249763] :irc.portlane.se 353 gak = #philosophy :a b @c
[1456249763] :irc.portlane.se 366 gak #philosophy :End of NAMES list.

"""