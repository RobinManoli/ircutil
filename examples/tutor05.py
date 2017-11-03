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
