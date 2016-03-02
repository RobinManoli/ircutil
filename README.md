# ircutil.py
Simplistic abstraction of IRC written in Python.

Very simple implementation that takes you very fast into coding your own stuff.

## Get Started
1. Make a copy of ./examples/get_started_bot.py to the same folder as README.md.
2. Edit your copy and add your irc server information.
3. Run the script and see that it connects to the server, joins the channel and responds to "hi".
4. Read and understand ./examples/get_started_bot.py.
5. Look at ./examples/tutorbot.py and start to implement your own stuff. Start with easy steps :)

## Features
- parses irc data into event objects (in a simple and slightly higher abstraction than IRC itself)
- parses multiple modes into single events (+oo becomes two separate op events)
- finds a free nick when nick in use when connecting to server
- reconnects (optionally) to server when disconnected
- works with ipv4 and ipv6
- works with python 2 and 3
- flood protection
- channel object which keeps track of ops, voices and normal users (half-ops not yet implemented)
- handles server's password and server specific args for password and ipv4/ipv6
	
## Todo
- create log function (maybe)
	
## Not Planned Features
- DCC chat/sends
