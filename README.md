Simplistic abstraction of IRC written in Python.

Very simple implementation that takes you very fast into coding your own stuff.

Features:
	- parses irc data into event objects
	- parses multiple modes into single events (+oo becomes two separate op events)
	- changes nick when nick in use when connecting to server
	- reconnects to server when disconnected
	- works with ipv4 and ipv6
	- works with python 2 and 3
	- flood protection
	
Todo:
	- handle passwords
	- create channel objects (maybe)
	- create log function (maybe)
	
Not Planned Features:
	- DCC chat/sends