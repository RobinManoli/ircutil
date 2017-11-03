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
    mybot.msg(event.chat, "prio 10")

@mybot.trigger("JOIN") # default priority is 0
def prio(event):
    mybot.msg(event.chat, "prio 0")

@mybot.trigger("JOIN", priority=30)
def prio30(event):
    mybot.msg(event.chat, "prio 30")

@mybot.trigger("JOIN", priority=-10)
def prio_10(event):
    mybot.msg(event.chat, "prio -10")

mybot.connect()
