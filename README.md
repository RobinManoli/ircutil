# ircutil.py
Simplistic abstraction of IRC written in Python.

Very simple implementation that takes you very fast into coding your own stuff.

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
    "See everything from irc server and ircutil"
    print (event.raw)
mybot.triggers.append(raw)
```


## Getting Started
Writing your own bot is as simple as this:
1. Make a copy of ./examples/get_started_bot.py to the same folder as README.md.
2. Edit your copy and add your IRC server information.
3. Run the script and see that it connects to the server, joins the channel and responds to "hi".
4. Read and understand the very simple ./examples/get_started_bot.py.

## Tutorial
Look at ./examples/tutorbot.py to see how to begin to implement your own stuff.

## Features
- parses irc data into event objects (in a simple and slightly higher abstraction than IRC itself)
- parses multiple modes into single events (+oo becomes two separate op events)
- finds a free nick when nick in use when connecting to server
- reconnects (optionally) to server list when disconnected
- works with ipv4 and ipv6
- works with python 2 and 3
- flood protection
- channel object which keeps track of modes, ops, voices and normal users (half-ops not yet implemented)
- handles server's password and server specific args for password and ipv4/ipv6
- emulate() function that reacts to raw IRC events written in a text file

## Not Planned Features
- DCC chat/sends
