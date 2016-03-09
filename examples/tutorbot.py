from __future__ import print_function
import ircutil


# NICK
mybot = ircutil.Connection()
mybot.nick = "pwnBot" # main nick
# list of alternative nicks (if mybot.nick is not available)
mybot.nicks = ['|pwnBot|', 'pwnBot^']
# There is also mybot._nick which contains that the current nick of the connection (when connected).
# Do not change the value of mybot._nick (becase it is prefixed with _). To change ._nick, use mybot.send.nick('newnick').

# USER DATA
mybot.ident = "ircutil" # ident in nick!ident@addr
mybot.realname = "ircutil for easily coding irc in python"

# SERVER
mybot.server = "irc.freenode.org:6665" # main server
# A ist of alternative servers with optional ports.
mybot.servers = ['irc.freenode.net:6666', 'irc.freenode.org']
# You can also specifically set ipv4/ipv6 and other optional args. See CONNECT.
# There is also mybot._server which contains the current connection's server.
# Do not change the value of mybot._server (becase it is prefixed with _).
mybot.password = '' # default password for mybot.server and mybot.servers
mybot.ipv6 = False # whether to use ipv6 as default when not specifying (False is the default value)
# Remember to connect at the bottom using: mybot.connect()


# TRIGGER FUNCTION EXAMPLES
def raw(event):
    """
    See everything from the irc server and ircutil.
    
    It looks something like this:
    >>> Connecting to irc.freenode.net:6666...
    >>> Connected!
    <<< NICK pwnBot
    <<< USER pwnBot ircutil ircutil :InfraUltra)))
    :sinisalo.freenode.net NOTICE * :*** Looking up your hostname...
    
    Explanation:
    >>> These lines are info from ircutil
    <<< These are raw IRC commands sent by ircutil
    The other data is the raw IRC data received from the IRC server.
    """
    print(event.raw)
    #print( vars(event) ) # you can use this instead of event.raw to see the full usage of the Event object
# After you create a function to trigger on IRC events, add it to the list mybot.triggers.
# Note that mybot.triggers.append adds the function to the end of the list,
# and each trigger function will run in order, from start to end.
# You can of course also use mybot.triggers.insert (Python List Insert Method)
# if you want to add your trigger functions in a different order.
mybot.triggers.append(raw)


def slave(event):
    """
    Perform raw IRC commands that owner sends in private such as
    !do JOIN #ircutil

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
    - (To learn raw IRC commands: connect your bot to an irc server, join a channel,
      and do some normal IRC stuff. Look at the output of print(event.raw), and there you have it. )
    - If you don't have a static IP, you can use event.ident in combination with
      for example event.host.endswith('-static-part-of-host.org').
      Use print( vars(event) ) to see the full content of the Event object.
    """
    if event.type == 'MSG' and not event.chan and event.host == 'static-ip.org' and event.msg.startswith('!do '):
        msg_split = event.msg.split(' ',1)
        if len(msg_split) > 1:
            cmd = msg_split[1]
            mybot.raw( cmd )
mybot.triggers.append(slave)


def auto_op(event):
    if event.type == 'JOIN':
        # add your ip here, or use event.nick, event.ident, event.host (or event.addr) for your own needs, as in nick!ident@host
        if event.host == 'static-ip.org':
            mybot.op(chan=event.chan, nick=event.nick)
mybot.triggers.append(auto_op)


def rejoin(event):
    "On 'KICK' the nick of the one being kicked is stored in event.target."
    if event.type == 'KICK':
        if event.target == mybot._nick:
            mybot.join(event.chan)
mybot.triggers.append(rejoin)


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
    
    Normally, event.type and event.cmd are the same.
    But since many IRC commands are numbers instead of words,
    ircutil names some of them (for example 'READY')
    for the code to be more clean and consistent.
    (For the full reference, look at the code in ircutil/event.py
    and search for self.type)
    
    So if you want to just use raw IRC commands, use event.cmd.
    If you want to use irscutil's abstraction, use event.type.
    """
    if event.type == 'READY':
        # triggers after nick and host are accepted, and are ready to chat

        # auto-join
        mybot.join('#ircutil')

        # uncomment to get a full view of the Connection object
        # print( vars(mybot) )
mybot.triggers.append(on_ready)


def claim(event):
    "Get op when channel gets empty (unless already has op)."
    # monitor QUIT, PART and KICK events
    if event.nick != mybot._nick and (event.type == 'QUIT' or event.type == 'PART' or event.type == 'KICK'):
        # create a list of channels to check (because the QUIT event doesn't have a channel)
        chans = [ event.chan.lower() ] if event.chan else mybot.chans.keys()
        for chan in chans:
            Chan = mybot.chans[chan]
            if len( Chan.all ) == 1 and not mybot._nick in Chan.ops:
                mybot.part( chan )
                mybot.join( chan )
          
    # note that you can use print( vars(mybot.chans['#mychan']) ) to get an overview of the Channel object
mybot.triggers.append(claim)


# CONNECT
# connect to irc, (reconnects when disconnected).
if __name__ == '__main__':
    mybot.connect()
# If you don't want to automatically reconnect, send the server parameter:
# mybot.connect('irc.freenode.net')
# Connections can handle certain args. These args also work for mybot.server and mybot.servers.
# mybot.connect('irc.freenode.net:6668') # with port
# mybot.connect('irc.freenode.net:6668 ipv6') # with port and server specific ipv6
# mybot.connect('irc.freenode.net ipv4') # with server specific ipv4
# mybot.connect('irc.freenode.net password=mypassword') # with server specific password
# mybot.connect('irc.freenode.net password=') # with server specific omitting password

# EMULATE CONNECTION
# If you want to test your script without connecting to a real server,
# you can use the mybot.emulate() method.
# It acts as receiving a set of raw IRC events written in a text file.
# Start by copy-pasting some raw IRC data into emulate.txt,
# and save it in the same folder as your script.
# Make sure emulate.txt contains events your script reacts to.
# Then comment any mybot.connect() lines, and uncomment this:
# mybot.emulate(emulate.txt)


# CONNECTION METHODS
"""
Use print( vars(mybot) ) for a full list!

mybot.ban('#mychan', '*!*@banned-user.com')

mybot.connect() # Connects to mybot.server, and if disconnected it connects to
                  mybot.servers.
                  If you don't want to automatically reconnect you can do a
                  simple connect by sending a server parameter:
                  mybot.connect('irc.freenode.net')
                  # mybot.connect('irc.freenode.net:6668') # or with port
                  # mybot.connect('irc.freenode.net:6668 ipv6') # or with port and server specific ipv6
                  # mybot.connect('irc.freenode.net ipv4') # or with server specific ipv4
                  # mybot.connect('irc.freenode.net password=mypassword') # or with server specific password
                  # mybot.connect('irc.freenode.net password=') # or with server specific omitting password

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

Use print( vars(event) ) for a full list!

event.addr is the nick!ident@hose of the one who performed the command,
           or the server currently connected to.

event.chan is the channel (or empty string if no channel was involved).

event.chat responds to corresponding chat room (either event.nick or event.chan)
           of the event.

event.cmd is the raw IRC command of the event, which is often the same as .type,
          but sometimes not (such as with mode event types and ircutil event types).

event._connection is a pointer to the connection of the event,
                  which can be used to access the connection
                  inside functions in separate files from your script:
                  def myoutsidefunc(event):
                      mybot = event._connection
                      mybot.quit()

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
