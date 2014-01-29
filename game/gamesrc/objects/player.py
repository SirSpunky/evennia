"""

Template module for Players

Copy this module up one level and name it as you like, then
use it as a template to create your own Player class.

To make the default account login default to using a Player
of your new type, change settings.BASE_PLAYER_TYPECLASS to point to
your new class, e.g.

settings.BASE_PLAYER_TYPECLASS = "game.gamesrc.objects.player.Player"

Note that objects already created in the database will not notice
this change, you have to convert them manually e.g. with the
@typeclass command.

"""
from ev import Player as DefaultPlayer


class Player(DefaultPlayer):
    def msg(self, text=None, from_obj=None, sessid=None, **kwargs):
        """
        Evennia -> User
        This is the main route for sending data back to the user from
        the server.

        text (string) - text data to send
        from_obj (Object/Player) - source object of message to send
        sessid - the session id of the session to send to. If not given,
          return to all sessions connected to this player. This is usually only
          relevant when using msg() directly from a player-command (from
          a command on a Character, the character automatically stores and
          handles the sessid).
        kwargs - extra data to send through protocol
                 """
        self.dbobj.msg(text=text+"\n", from_obj=from_obj, sessid=sessid, **kwargs)
