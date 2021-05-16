# Python Ircutil
Simplistic, powerful and lightweight abstraction of IRC, written in Python.

The point of this utility is to connect to IRC and take you very fast into coding your own stuff.
The only magic that happens is that Ircutil connects, stays connected (and optionally reconnects).


## Features
- parses IRC data into easy-to-use event objects
- parses multiple IRC channel modes into single events (+oo becomes two separate op events)
- finds a free nick when nick in use when connecting to server
- reconnects (optionally) to server list when disconnected
- channel objects which keep track of modes, ops, voices and normal users (half-ops not yet implemented)
- handles server's password and server specific args for password and ipv4/ipv6
- handles ctcp sending and replying
- emulate() function that acts as receiving a set of raw IRC events written in a text file
- works with ipv4 and ipv6
- works with python 2 and 3
- simple flood protection
- can be used both to create bots and clients


## Not Included (Nor Planned)
- DCC chat/sends
- Threads
- SSL/TLS


# Tutorial
This tutorial is based on Python 3. If you want to use Python 2 you can change the shebang to something like:
```
#! /usr/bin/env python2.7
```
and make print work as a function (add this line under the shebang above):
```
from __future__ import print_function
```


## Getting Started
The first thing to do is only to connect to IRC (to make sure you have the right IRC server address and your IRC ports open), from examples/tutor01.py:
```
#!/usr/bin/python3

"""
Simplistic bot that connects to IRC and prints what happens.
"""

import ircutil

mybot = ircutil.Connection() # create a connection

# bot setup
mybot.nick = "ezBot" # the bot's nick
mybot.server = "irc.freenode.org" # the server to connect to

# handle IRC events
@mybot.trigger() # run the function below on all IRC events
def raw(event):
    # See everything from IRC server and ircutil
    print(event.raw) # print the event as raw, unprocessed text

# now connect to IRC, stay connected and reconnect automatically
mybot.connect()
```
When you run the code above you should see some text printed on the screen, similar to what you see when you connect with an IRC client.
There might be a lot of text if you wait for the bot to connect fully. The text might look something like this:
```
:card.freenode.net NOTICE * :*** Looking up your hostname...
:card.freenode.net NOTICE * :*** Checking Ident
:card.freenode.net NOTICE * :*** Found your hostname
```
Press CTRL+C to stop the bot.


## Handling Events
IRC is based on events such as joins, quits, messages, modes and so on.
Ircutil handles events mainly with trigger decorators, as you could see in the previous example.
So when you want a function to run on all IRC events, you decorate it like this:
```
@mybot.trigger()
```
Usually however, you only want your function to run on certain events, with certain conditions. To do that you use the event object inside a lambda function:
```
@mybot.trigger(lambda event: event.MSG)
def myfunc(event):
    ...
```
A lambda function is used because you want to wait until the event happens before you run the function.

For example, event.MSG is True if the event is a message (PRIVMSG in raw IRC, which also includes channel messages and CTCP requests).
The function myfunc is only called on events where the lambda function evaluates as true - in this case if the event is a message.

In the simple case above, the function runs on all message events.
If there are no other conditions than to run on a single type of event, you can remove the lambda and simplify the decorator above like this:
```
@mybot.trigger("MSG")
def myfunc(event):
    ...
```

Here is some basic usage of handling events, from examples/tutor02.py:
```
#!/usr/bin/python3

import ircutil

mybot = ircutil.Connection()
mybot.nick = "ezBot"
mybot.server = "irc.freenode.org"

@mybot.trigger()
def raw(event):
    # See everything from irc server and ircutil
    print(event.raw)


# --- new code starts here ---

# Run the function below on welcome events.
# The welcome event happens when you are fully connected on IRC.
@mybot.trigger(lambda event: event.WELCOME)
def autojoin(event):
    mybot.join('#ircutil') # join an IRC channel

# Run the function below on message events, respond when the message is "hi"
@mybot.trigger(lambda event: event.MSG and event.msg == "hi")
def respond(event):
    # event.chat is either the channel of the event,
    # or if it was a private message - the nickname of the user who sent the message
    mybot.msg(chat=event.chat, msg="%s: hi" %event.nick)

# Run the function below on join events except when mybot joins a channel
# mybot._nick is the actual current nick, whereas mybot.nick is the primary,
# desired nick attempted to use on connect
@mybot.trigger(lambda event: event.JOIN and event.nick != mybot._nick)
def greet(event):
    mybot.msg(chat=event.chan, msg="%s: hi" %event.nick)

# Run the function below when mybot is kicked
# mybot._nick is the actual current nick, whereas mybot.nick is the primary,
desired nick attempted to use on connect
@mybot.trigger(lambda event: event.KICK and event.target == mybot._nick)
def rejoin(event):
    mybot.join(event.chan)

# Run the function below when receiving a CTCP request.
# Also note that CTCP requests are treated as messages, so event.MSG is True too.
@mybot.trigger(lambda event: event.CTCP)
def ctcp_reply(event):
    # event.chat is either the channel of the event,
    # or if it was a private message - the nickname of the user who sent the message
    mybot.ctcp(event.chat, event.ctcp, "my CTCP", reply=True) # do a CTCP reply
    mybot.ctcp(event.chat, event.ctcp) # make a CTCP request
    print(event.chat, "%s just sent a CTCP %s" % (event.nick, event.msg))

# Run the function below when a topic is set.
@mybot.trigger("TOPIC") # short for lambda event: event.TOPIC
def topic(event):
    # print the newly set topic
    print("new topic set:", event.msg)

# Run the function below when someone does a /me action
@mybot.trigger("ACTION") # short for lambda event: event.ACTION
def imitate(event):
    mybot.ctcp(event.chat, event.ctcp, "too %s" % event.msg)

# --- new code ends here ---


# connect to IRC
mybot.connect()
```


## Emulating IRC
When writing an IRC bot or script you usually want to test it often.
Instead of setting up your own server and connecting to IRC all the time you can use the emulator function of ircutil, as it is much faster.

To use the emulator you need to have a text file of the IRC data to process.
The IRC events which the previous bot of the tutorial triggered are stored at ircutil/examples/ircdata.txt - by just copy-pasting them from bot output text.

Using the same code as the bot above, but changing mybot.connect() to mybot.emulate('ircdata.txt') will run the text data as if it were coming from an IRC server.

Make sure to use the correct path for ircdata.txt.

Also, note that when copy-pasting a CTCP request from the bot output, there are some hidden instances of the character '\x01' or chr(1) that might be lost.
In ircdata.txt they have been added there with this command:
```
sed -i -e "s/ezBot \:VERSION/ezBot \:\x01VERSION\x01/" ircdata.txt
```
You can find the code in examples/tutor03.py.


## Background Processing
If you are coding a bot and want it to output something after a specific amount of time,
you might need background processing.
Using time.sleep() might work in some cases, but it would stop all other processing,
and sometimes it could even disconnect your bot with a ping timeout.

This problem is solved using the @background decorator:
```
@mybot.background()
def my_background_func():
    # this function will be called every second by default
    ...
```

How often background functions will be called are based on Python sockets' timeout setting.
To set the frequency to run every 5 seconds instead, you can use:
```
mybot.socket_timeout = 5 # or you can even use 0.1 to call 10 times per second
```

And if you want more control of the order of calling the background processes,
you can use priority in the same way as for triggers:
```
@mybot.background()
def my_background_func():
    # this function will be called last, since default priority is 0
    print('priority 0 - default')

@mybot.background(priority=10)
def my_background_func2():
    # this function will be called first, since it has the highest priority
    print('priority 10')

```

## User and Server Setup and Data
Example code from examples/tutor04.py:
```
#!/usr/bin/python3

import ircutil

mybot = ircutil.Connection()
mybot.nick = "ezBot"
mybot.server = "irc.freenode.org:6665"

# get current nick with mybot._nick
mybot.nicks = ['|ezBot|', 'ezBot^'] # list of alternative nicks (if mybot.nick is not available)
mybot.ident = "ircutil" # ident in nick!ident@addr
mybot.realname = "ircutil for easily coding irc in python"

# list of alternative servers with optional ports.
# there is also mybot._server which contains the current connection's server
mybot.servers = ['irc.freenode.net:6666', 'irc.freenode.net']
mybot.password = '' # default password for mybot.server and mybot.servers
mybot.ipv6 = False # whether to use ipv6 as default when not specifying (False is the default value)
mybot.autojoin = ['#mychan1', '+mychan2'] # join these channels automatically

#mybot.raw_output = None # do not automatically display anything, this is the default setting
#mybot.raw_output = True # automatically display everything from irc
#mybot.raw_output = lambda event: "my output string: %s" % event.raw # display everything in a custom format
#mybot.raw_colored_output = True # same as above, but colors will be added -- should work on *nix including OS X, linux and windows (provided you use ANSICON, or in Windows 10 provided you enable VT100 emulation) (https://stackoverflow.com/a/287944)
#mybot.raw_output_display_motd = False # whether to display motd when using above functions

# --- triggers ---

# Get user data when sending an !about message
@mybot.trigger(lambda event: event.MSG and event.msg == "!about")
def about(event):
    mybot.notice(event.chat, "your nick is %s" % event.nick)
    mybot.msg(event.chat, "your addr is %s" % event.addr)
    mybot.msg(event.chat, "your ident is %s" % event.ident)
    mybot.msg(event.chat, "your host is %s" % event.host)

# Run the function below when a message that starts with !nick is received,
# and make sure there is text data after the text !nick
@mybot.trigger(lambda event: event.MSG and event.msg.startswith("!nick") and len(event.msg.strip()) > len("!nick"))
def change_nick(event):
    # change nick to the text after !nick
    newnick = event.msg.split()[1]
    mybot.newnick(newnick)


mybot.connect()
```

## Channel Modes
Note that mybot.chans contains all channels that mybot is in, with all users. See the reference below.
```
#!/usr/bin/python3

import ircutil
import fnmatch

mybot = ircutil.Connection()
mybot.nick = "ezBot"
mybot.server = "irc.freenode.org:6665"

@mybot.trigger()
def raw(event):
    # See everything from irc server and ircutil
    print(event.raw)

@mybot.trigger(lambda event: event.WELCOME)
def autojoin(event):
    mybot.join('#ircutil')

# trigger on chan modes set by others
@mybot.trigger(lambda event: event.MODE and event.nick != mybot._nick)
def mode(event):
    # imitate mode just being set
    mybot.mode(event.mode, event.chan, event.target)

# create a set of masks with corresponding modes
# this is for the purpose of this tutorial
# should be using a database so that new masks are saved
# and can be added when the bot is still connected
masks = dict()
masks["*"] = "+v" # give voice to everyone
masks["*!*@op-ip-addr.com"] = "+o" # give op to this ip/domain
masks["*!*@ban-ip-addr.com"] = "+b" # ban this ip/domain
@mybot.trigger("JOIN")
def auto_mode(event):
    for mask in masks.keys():
        if fnmatch.fnmatch( event.addr, mask ):
            mode = masks[mask] # +v or +o or +b
            if 'b' in mode:
                mybot.mode(mode, event.chan, mask)
            else:
                # you could more explicitly use mybot.op, mybot.deop, etc
                mybot.mode(mode, event.chan, event.nick)

# get op back in empty channel, if op has been lost
# monitor QUIT, PART and KICK events
@mybot.trigger(lambda event: event.nick != mybot._nick and (event.QUIT or event.PART or event.KICK))
def claim(event):
    # on part and kick events, only the channel where it occurred needs to be checked
    # but for quit events, all channels with the user who quit must be checked
    # so, create a list of channels to check
    chans = [ event.chan.lower() ] if event.chan else mybot.chans.keys()
    for chan in chans:
        Chan = mybot.chans[chan] # get the channel object
        # Chan.all contains all users of the channel, and Chan.ops contains all ops
        # so if there is only one user and mybot doesn't have op, cycle the chan
        if len( Chan.all ) == 1 and not mybot._nick in Chan.ops:
            mybot.part( chan )
            mybot.join( chan )

mybot.connect()
```


## Priority
Normally the triggers run in the order the are written. The earlier they appear in the script the earlier they trigger.
In case you want your functions to trigger in another order you can set their priorities.
The higher the number you set as priority, the earlier that function will trigger.

If you don't set any priority the default value is 0.
Functions with the same priority will trigger in the order they appear in the script, top first.
```
#!/usr/bin/python3

import ircutil

mybot = ircutil.Connection()
mybot.nick = "ezBot"
mybot.server = "irc.freenode.org:6665"

@mybot.trigger()
def raw(event):
    # See everything from irc server and ircutil
    print(event.raw)

@mybot.trigger("WELCOME")
def autojoin(event):
    mybot.join('#ircutil')

@mybot.trigger("JOIN", priority=10)
def prio10(event):
    mybot.msg(event.chat, "called second - prio 10")

@mybot.trigger("JOIN") # default priority is 0
def prio(event):
    mybot.msg(event.chat, "called third - prio 0")

@mybot.trigger("JOIN", priority=30)
def prio30(event):
    mybot.msg(event.chat, "called first - prio 30")

@mybot.trigger("JOIN", priority=-10)
def prio_10(event):
    mybot.msg(event.chat, "called last - prio -10")

mybot.connect()
```


## Custom Connection Loops
If you don't want Ircutil to automatically reconnect, send the server parameter:
```
mybot.connect('irc.freenode.net')
```
Connections can handle certain args. These args also work for mybot.server and mybot.servers.
```
mybot.connect('irc.freenode.net:6668') # with port
mybot.connect('irc.freenode.net:6668 ipv6') # with port and server specific ipv6
mybot.connect('irc.freenode.net ipv4') # with server specific ipv4
mybot.connect('irc.freenode.net password=mypassword') # with server specific password
mybot.connect('irc.freenode.net password=') # with server specific omitting password
```

## Going Deeper
To learn more about the Ircutil and its events you can use vars(mybot) on the event.WELCOME, vars(event) for any event you want to know more about, and vars(mybot.chans) to see channel data.


# Reference

## IRC Commands
```
print( vars(mybot) ) # for a full list!

mybot.ban('#mychan', '*!*@banned-user.com')

mybot.connect() # Connects to mybot.server, and if disconnected it connects to mybot.servers.
# If you don't want to automatically reconnect,
# you can do a simple connect by sending a server parameter: mybot.connect('irc.freenode.net')
# mybot.connect('irc.freenode.net:6668') # or with port
# mybot.connect('irc.freenode.net:6668 ipv6') # or with port and server specific ipv6
# mybot.connect('irc.freenode.net ipv4') # or with server specific ipv4
# mybot.connect('irc.freenode.net password=mypassword') # or with server specific password
# mybot.connect('irc.freenode.net password=') # or with server specific omitting password

# Sendsa ctcp command. If reply is set to True, it will be a ctcp reply.
mybot.ctcp('nick', 'VERSION', msg='', reply=False)

mybot.deop('#mychan', 'nick')

mybot.devoice('#mychan', 'nick')

# Send text to event handler.
# Can be used instead of print and handled the same way as other events.
mybot.echo('my message')

mybot.join('#mychan')

mybot.me('#mychan', 'my message') # First parameter can also be a nick.

mybot.msg('#mychan', 'my message') # First parameter can also be a nick.

mybot.mode('+k', '#mychan', 's3cr3t') # First parameter can also be mybot's nick.

# Send IRC nick command. Changes nick if newnick is available. Current nick is availabe as mybot._nick
mybot.newnick('newnick')

mybot.notice('#mychan', 'my message') # First parameter can also be a nick.

mybot.op('#mychan', 'nick')

mybot.part('#mychan', 'my message')

mybot.voice('#mychan', 'nick')

mybot.raw('JOIN #mychan') # Send a raw IRC command.

mybot.topic('#mychan', 'my topic')

mybot.unban('#mychan', '*!*@banned-user.com')

mybot.quit('my message')
```


## Event Booleans
```
print( vars(event) ) # for a full list!

self.ACTION # True on /me actions
self.BAN 
self.CTCP # True on CTCP requests and /me actions
self.CTCP_REPLY
self.DEOP 
self.DEVOICE 
self.DEHALFOP 
self.ECHO 
self.ERROR 
self.HALFOP 
self.JOIN 
self.KICK 
self.MODE 
self.MSG ¤ True on chat messages and CTCP requests
self.NAMREPLY 
self.NICK 
self.NOTICE # True on notices and CTCP replies
self.OP 
self.PART 
self.PING 
self.PRIVMSG 
self.QUIT 
self.SENT # True when Ircutil sent an IRC command
self.TOPIC 
self.UNBAN 
self.VOICE 
self.WELCOME 
```

## IRC Event Data
```
# the nick!ident@hose of the one who performed the command, or the server currently connected to.
event.addr

event.chan # is the channel (or empty string if no channel was involved).

event.chat # responds to corresponding chat room (either event.nick or event.chan) of the event.

event.ctcp # the ctcp type (VERSION, ACTION, etc) on CTCP requests/replies

# pointer to the connection of the event,
# which can be used to access the connection inside functions in separate files from your script:
event._connection
def myoutsidefunc(event):
    mybot = event._connection
    mybot.quit()

event.host # is the host (in nick!ident@host) of event.addr.

event.ident # is the ident (in nick!ident@host) of event.addr.

event.mode # is the mode being set

event.msg # is the message text of a message, ctcp request, or the topic text, or kick/ban text.

event.newnick # is the new nick being set

event.nick # is the nick of the one who performed the event (or empty string if no other user was involved).

event.target
# is the nick of the one being kicked on the KICK event.
# is the nick of the one receiving OP/DEOP/VOICE/DEVOICE.
# is the mask for the BAN/UNBAN events (or other events with masks).
# is the key for the KEY event.
# is the new nick on the NICK event

# the raw IRC command of the event,
# which is usually a capital word (such as JOIN or QUIT), but sometimes a number
event.type

```

## The Channel Objects
A Connection contains all joined channels in .chans (such as mybot.chans), where .chans is a dictionary, and the keys are the channel names in lower case.
Each channel contains a channel object such as this:
```
self.chan = chan # channel name
self.ops = [] # list of channel ops
self.halfops = []
self.voices = []
self.users = []
self.all = [] # list of all channel users
self.topic = ""
self.topicsetter = ""
self.topictime = None
self.modes = ""
self.k = '' # key
self.b = [] # bans

```
