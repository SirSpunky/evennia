
######################################################################
# Evennia MU* server configuration file
#
# You may customize your setup by copy&pasting the variables you want
# to change from the master config file src/settings_default.py to
# this file. Try to *only* copy over things you really need to customize
# and do *not* make any changes to src/settings_default.py directly.
# This way you'll always have a sane default to fall back on
# (also, the master config file may change with server updates).
#
######################################################################

from src.settings_default import *

######################################################################
# Custom settings
######################################################################
BASE_OBJECT_TYPECLASS = "game.gamesrc.objects.object.Object"
BASE_CHARACTER_TYPECLASS = "game.gamesrc.objects.character.Character"
BASE_ROOM_TYPECLASS = "game.gamesrc.objects.room.Room"
BASE_EXIT_TYPECLASS = "game.gamesrc.objects.exit.Exit"
BASE_PLAYER_TYPECLASS = "game.gamesrc.objects.player.Player"
BASE_CHANNEL_TYPECLASS = "game.gamesrc.comms.comms.Channel"

# Command set used on session before player has logged in
CMDSET_UNLOGGEDIN = "game.gamesrc.cmdsets.cmdset_unloggedin.UnloggedinCmdSet"
# Command set used on the logged-in session
CMDSET_SESSION = "game.gamesrc.cmdsets.cmdset_session.SessionCmdSet"
# Default set for logged in player with characters (fallback)
CMDSET_CHARACTER = "game.gamesrc.cmdsets.cmdset_character.CharacterCmdSet"
# Command set for players without a character (ooc)
CMDSET_PLAYER = "game.gamesrc.cmdsets.cmdset_player.PlayerCmdSet"

AT_SERVER_STARTSTOP_MODULE = "game.gamesrc.conf.at_server_startstop"

SEARCH_AT_RESULT = "game.gamesrc.comms.cmdparser.at_search_result"
CONNECTION_SCREEN_MODULE = "game.gamesrc.comms.connection_screen"

# Different Multisession modes allow a player (=account) to connect to the
# game simultaneously with multiple clients (=sessions). In modes 0,1 there is
# only one character created to the same name as the account at first login.
# In modes 1,2 no default character will be created and the MAX_NR_CHARACTERS
# value (below) defines how many characters are allowed.
#  0 - single session, one player, one character, when a new session is
#      connected, the old one is disconnected
#  1 - multiple sessions, one player, one character, each session getting
#      the same data
#  2 - multiple sessions, one player, many characters, each session getting
#      data from different characters
MULTISESSION_MODE = 0

MEDIA_ROOT = os.path.join(GAME_DIR, 'web', 'media')

# How long time (in seconds) a user may idle before being logged
# out. This can be set as big as desired. A user may avoid being
# thrown off by sending the empty system command 'idle' to the server
# at regular intervals. Set <=0 to deactivate idle timout completely.
IDLE_TIMEOUT = 0

######################################################################
# SECRET_KEY was randomly seeded when settings.py was first created.
# Don't share this with anybody. It is used by Evennia to handle
# cryptographic hashing for things like cookies on the web side.
######################################################################
SECRET_KEY = 'z/^)"R"]Bl=ZrN7QCbtaE1`p5&|Pn0XHJ!U#,}8W'

