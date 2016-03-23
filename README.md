# ircutil.py
Simplistic abstraction of IRC written in Python.

Very simple implementation that takes you very fast into coding your own stuff.

## Features
- parses IRC data into event objects (in a simple and slightly higher abstraction than IRC itself)
- parses multiple modes into single events (+oo becomes two separate op events)
- finds a free nick when nick in use when connecting to server
- reconnects (optionally) to server list when disconnected
- channel object which keeps track of modes, ops, voices and normal users (half-ops not yet implemented)
- handles server's password and server specific args for password and ipv4/ipv6
- emulate() function that acts as receiving a set of raw IRC events written in a text file
- works with ipv4 and ipv6
- works with python 2 and 3
- flood protection
- can be used both to create bots and clients

## Example Code
Setting up a bot:
```
import ircutil

mybot = ircutil.Connection()
mybot.nick = "ezBot" # main nick
mybot.server = "irc.freenode.org" # main server
```
Next, create a function that displays all IRC data, and add it to triggers:
```
def raw(event):
    "See everything from IRC server and ircutil"
    print (event.raw)
mybot.triggers.append(raw)
```
Now, respond to anyone saying hi (in private or channel):
```
def respond(event):
    if event.MSG and event.msg == "hi":
        # chat and event.chat refers to either a channel or nickname,
        # to send the message to
        mybot.msg(chat=event.chat, msg=event.nick + ": hi")
mybot.triggers.append(respond)
```
And connect to IRC:
```
mybot.connect()
```


## Getting Started

1. Make a copy of examples/get_started_bot.py to the same folder as README.md.
2. Edit your copy and add your IRC server information.
3. Run the script and see that it connects to the server, joins the channel and responds to "hi".


## Tutorial

1. Read and understand the very simple examples/get_started_bot.py
2. Read, understand and try out examples/tutorbot.py (read the whole file).
3. Create trigger functions that print vars(event), vars(mybot) and vars(mybot.chans) to get a good overview of ircutil.
4. Learn to use mybot.emulate() (see tutorbot.py) instead of mybot.connect() to test your scripts.


## Not Included (Nor Planned)
- DCC chat/sends
- Threads
- SSL/TLS
