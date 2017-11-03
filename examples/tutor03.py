#!/usr/bin/python3

import ircutil

mybot = ircutil.Connection()
mybot.nick = "ezBot"
mybot.server = "irc.freenode.org"

# --- moved and edited the raw function down to new code ---

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
# desired nick attempted to use on connect
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

# --- new code starts here ---

@mybot.trigger()
def raw(event):
    # since the emulator already prints out raw irc data, only print out ircutil data
    # which starts with <<< (sent IRC commands) or >>> (info from Ircutil)
    if event.raw.startswith(('<<<','>>>')):
        print(event.raw)

# emulate IRC
mybot.emulate('ircdata.txt')
#mybot.emulate('/path/to/ircdata.txt') # you can use the absolute path
