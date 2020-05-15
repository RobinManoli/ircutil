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
#self.raw_output_display_motd = False # whether to display motd when using above functions

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
