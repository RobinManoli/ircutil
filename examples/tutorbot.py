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
    "See everything from irc server and ircutil."
    print (event.raw)
mybot.triggers.append(raw)

def slave(event):
    """
    Perform raw IRC commands that owner sends in private such as
    '!do JOIN #ircutil".

    Explicitly:
    On chat messages ('MSG'),
    though only private (not event.chan),
    when sent from my ip (event.host),
    and the message starts with "!do ",
    perform the command as a raw IRC command.

    Note:
    - Use this trigger with caution! It will give full control of your bot to anyone
      with the given host!
    - You have to use raw IRC commands, and not normal client commands.
    - If you don't have a static IP, you can use event.ident in combination with
      for example event.host.endswith('-static-part-of-host.org')
    """
    if event.type == 'MSG' and not event.chan and event.host == 'static-ip.org' and event.msg.startswith('!do '):
        msg_split = event.msg.split(' ',1)
        if len(msg_split) > 1:
            cmd = msg_split[1]
            mybot.raw( cmd )
mybot.triggers.append(slave)


def auto_op(event):
    if event.type == 'JOIN':
        if event.host == 'static-ip.org': # add your ip here, or use event.nick, event.ident, event.host (or event.addr) for your own needs, as in nick!ident@host
            mybot.op(chan=event.chan, nick=event.nick)
mybot.triggers.append(auto_op)


def rejoin(event):
    "On 'KICK' the nick of the one being kicked is event.target."
    if event.type == 'KICK':
        if event.target == mybot._nick:
            mybot.join(event.chan)
mybot.triggers.append(rejoin)


def claim(event):
    "part and join chan if alone and not op"
    if event.nick != mybot._nick and (event.type == 'QUIT' or event.type == 'PART' or event.type == 'KICK'):
        chan = mybot.chans[event.chan.lower()]
        if len( chan.all ) == 1 and not mybot._nick in chan.ops:
            mybot.part( event.chan )
            mybot.join( event.chan )
mybot.triggers.append(claim)


def on_msg(event):
    "'MSG' triggers on a channel or private text message."
    if event.type == 'MSG':
        if event.msg == 'hi' and event.chan.lower() == '#ircutil':
            mybot.msg(chat=event.chat, msg="hi %s :)" % event.nick)
            #mybot.msg(chat=event.chan, msg="hi %s :)" % event.nick) # alternative code

        # use not event.chan for private messages
        elif event.msg == 'hi' and not event.chan:
            mybot.msg(chat=event.chat, msg="hi :)")
            #mybot.msg(chat=event.nick, msg="hi :)") # alternative code
mybot.triggers.append(on_msg)


def on_ready(event):
    """
    'READY' triggers on the raw IRC welcome event (001),
    when your nick and host are accepted, and you are ready to chat.
    """
    if event.type == 'READY':
        mybot.join('#ircutil')
mybot.triggers.append(on_ready)

# connect to irc
mybot.connect()




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
          but sometimes not (such as with mode event types and ircutil event types).

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
