# IMPORT
import ircutil as irc


# SETUP
mybot = irc.Connection()
mybot.nick = "pwnBot" # main nick
# list of alternative nicks (if .nick not available)
mybot.nicks = ['|pwnBot|', 'pwnBot^']
# There is also mybot._nick which contains that currently set nick.
# Do not change members that start with _! use mybot.send.nick('newnick').



mybot.server = "irc.freenode.org:6665" # main server
# list of alternative servers with optional ports
mybot.servers = ['irc.freenode.net:6666', 'irc.freenode.org']
# There is also mybot._server which contains the current connection's server.
# Do not change members that start with _!

# Remember to connect at the bottom using: mybot.connect()
# which connects and reconnects when disconnected.

# TRIGGER EXAMPLES
def raw(event):
    "See everything from irc server and irc.py."
    print (event.raw)
mybot.triggers.append(raw)

def slave(event):
    """
    Perform raw IRC commands that owner sends in private such as
    '!do JOIN #irc.py".

    Explicitly:
    On chat messages (irc.MSG),
    though only private (not event.chan),
    when sent from my ip (event.host),
    and the message starts with "!do ",
    perform the command as a raw IRC command.

    Note:
    - This trigger is a security risk! It's meant only to get you started,
    but should be removed once your bot goes public.
    - You have to use raw IRC commands, and not normal client commands.
    - If you don't have a static IP, you can use event.ident in combination with
    for example event.host.endswith('-static-part-of-host.org')
    """
    if event.type == irc.MSG and not event.chan and event.host == 'my-static-ip.org' and event.msg.startswith('!do '):
        msg_split = event.msg.split(' ',1)
        if len(msg_split) > 1:
            cmd = msg_split[1]
            mybot.raw( cmd )
mybot.triggers.append(slave)


on_join(event):
    if event.type == irc.JOIN:
        if event.host == 'static-ip.org':
            pass
            #mybot.op(chan=event.chan, nick=event.nick) #todo
mybot.triggers.append(on_join)

on_kick(event):
    "On irc.KICK the nick of the one being kicked is event.target."
    if event.type == irc.KICK:
        if event.target == mybot._nick:
            pass
            #mybot.op(chan=event.chan, nick=event.nick) #todo
mybot.triggers.append(on_join)


on_msg(event):
    "irc.MSG triggers on a channel or private text message."
    if event.type == irc.MSG:
        if event.msg == 'hi' and event.chan.lower() == '#irc.py':
            mybot.msg(chat=event.chat, msg="hi %s :)" % event.nick)
            #mybot.msg(chat=event.chan, msg="hi %s :)" % event.nick)

        elif event.msg == 'hi' and not event.chan:
            mybot.msg(chat=event.chat, msg="hi :)")
            #mybot.msg(chat=event.nick, msg="hi :)")
mybot.triggers.append(on_msg)

on_ready(event):
    """
    irc.READY triggers on the raw IRC welcome event (001),
    when your nick and host are checked, and you are ready to chat.
    """
    if event.type == irc.READY:
        mybot.join('#irc.py')
mybot.triggers.append(on_ready)






# CONNECTION METHODS
"""
mybot.ban('#mychan', '*!*@banned-user.com')

mybot.connect() # Connects to mybot.server, and if disconnected it connects to
                  mybot.servers.
                  If you don't want to automatically reconnect you can do a
                  simple connect by sending a server parameter:
                  mybot.connect('irc.freenode.net')

mybot.ctcp('nick', 'VERSION', msg='', reply=False) # Sends a ctcp command.
                                                     If reply is set to True,
                                                     it will be a ctcp reply.

mybot.deop('#mychan', 'nick')

mybot.devoice('#mychan', 'nick')

mybot.echo('my message') # Sends text to event handler. Can be used instead of
                           print and handled the same way as other events.
mybot.join('#mychan')

mybot.me('#mychan', 'my message') # First parameter can also be a nick.

mybot.msg('#mychan', 'my message') # First parameter can also be a nick.

mybot.mode('+k', '#mychan', 's3cr3t') # First parameter can also be mybot's nick.

mybot.send.nick('newnick') # Send IRC nick command.
                             Changes nick if newnick is available.
                             Note that mybot.nick is the primary nickname.

mybot.notice('#mychan', 'my message') # First parameter can also be a nick.

mybot.op('#mychan', 'nick')

mybot.part('#mychan', 'my message')

mybot.voice('#mychan', 'nick')

mybot.raw('JOIN #mychan') # Send a raw IRC command.

mybot.topic('#mychan', 'my topic')

mybot.unban('#mychan', '*!*@banned-user.com')

mybot.quit('my message')

"""


# EVENT MEMBERS
"""

event.addr is the nick!ident@hose of the one who performed the command,
           or the server currently connected to.

event.chan is the channel (or empty string if no channel was involved).

event.chat responds to corresponding chat room (either event.nick or event.chan)
           of the event.

event.cmd is the raw IRC command of the event, which is often the same as .type,
          but sometimes not (such as with mode event types and irc.py event types).

event.host is the host (in nick!ident@host) of event.addr.

event.ident is the ident (in nick!ident@host) of event.addr.

event.msg is the message text.

event.nick is the nick of the one who performed the event
           (or empty string if no other user was involved).

event.target
            is the nick of the one being kicked on the KICK event.
            is the nick of the one receiving OP/DEOP/VOICE/DEVOICE.
            is the mask for the BAN/UNBAN events (or other events with masks).
            is the key for the KEY event.

"""