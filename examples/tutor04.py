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

# --- triggers ---

@mybot.trigger()
def raw(event):
    # See everything from irc server and ircutil
    print(event.raw)

@mybot.trigger(lambda event: event.WELCOME)
def autojoin(event):
    mybot.join('#ircutil')

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
