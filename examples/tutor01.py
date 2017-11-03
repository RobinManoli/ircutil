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
