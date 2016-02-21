import ircutil as irc

mybot = irc.Connection()
mybot.nick = "ezBot" # main nick
mybot.server = "irc.freenode.org" # main server

def raw(event):
    "See everything from irc server and irc.py."
    print (event.raw)
mybot.triggers.append(raw)

def autojoin(event):
    "Join a channel when connected and ready."
    if event.type == irc.READY:
        mybot.join('#irc.py')
mybot.triggers.append(autojoin)

def respond(event):
    if event.type == irc.MSG and event.msg == ("hi"):
        mybot.msg(chat=event.chat, msg="%s: hi" %event.nick)
mybot.triggers.append(respond)

mybot.connect()
