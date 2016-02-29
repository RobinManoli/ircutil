from ircutil.connection import Connection

# IRC EVENTS
#ACTION = 'ACTION'
#ERROR = 'ERROR'
#JOIN = 'JOIN'
#KICK = 'KICK'
#MODE = 'MODE'
#MSG = 'PRIVMSG'
#NICK = 'NICK'
#NOTICE = 'NOTICE'
#PART = 'PART'
#READY = 'READY' # welcome event, when allowed inside the server to chat
#TOPIC = 'TOPIC'
#QUIT = 'QUIT'

# MODES
#OP = 'OP'
#DEOP = 'DEOP'
#VOICE = 'VOICE'
#DEVOICE = 'DEVOICE'
#BAN = 'BAN'
#UNBAN = 'UNBAN'

# irc.py events
#DISCONNECTED = 'DISCONNECTED' # when connection lost from server, use as event.msg.startswith(irc.DISCONNECTED)
#ECHO = 'ECHO' # following data was echoed, stored as event.msg
#SENT = 'SENT' # following data was sent to irc server, stored as event.msg
