import logging
import pathlib

# This is a minimal configuration to get you started with the Text mode.
# If you want to connect Errbot to chat services, checkout
# the options in the more complete config-template.py from here:
# https://raw.githubusercontent.com/errbotio/errbot/master/errbot/config-template.py

BACKEND = 'Text'  # Errbot will start in text mode (console only mode) and will answer commands from there.

BOT_DIR = pathlib.Path( '/home/gberr097/Documents/ntnu-errbot/errbot' )
#BOT_DIR = pathlib.Path( r'D:/Scratch/NTNU-ErrBot/errbot' )

BOT_DATA_DIR =  BOT_DIR / 'data'
BOT_EXTRA_PLUGIN_DIR = BOT_DIR / 'plugins'

BOT_LOG_FILE = BOT_DIR / 'errbot.log'
BOT_LOG_LEVEL = logging.DEBUG

if BACKEND == "IRC":
    BOT_ADMINS = ('jkbrune100!~u@*', 'blue!~u@*' )  # !! Don't leave that to "@CHANGE_ME" if you connect your errbot to a chat system !!

    BOT_IDENTITY = {
        'nickname' : 'blue',
        'server' : 'irc.ergo.chat',
        'username' : '',
        'password' : 'blue:6jfzDKPdZpHkVi6w2deF', 
        'port' : 6697,
        'ssl' : True,
    }
elif BACKEND == "Text":
    BOT_ADMINS = ('@jkbrune100')

    BOT_IDENTITY = {
        'nickname': '@blue'
    }

BOT_ALT_PREFIXES = ('Blue','blue')
BOT_ALT_PREFIX_SEPARATORS = (':', ',', ';',' ')

CHATROOM_PRESENCE = ("#ntnuerc",)
