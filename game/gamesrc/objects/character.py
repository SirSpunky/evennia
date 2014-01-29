"""

Template for Characters

Copy this module up one level and name it as you like, then
use it as a template to create your own Character class.

To make new logins default to creating characters
of your new type, change settings.BASE_CHARACTER_TYPECLASS to point to
your new class, e.g.

settings.BASE_CHARACTER_TYPECLASS = "game.gamesrc.objects.mychar.MyChar"

Note that objects already created in the database will not notice
this change, you have to convert them manually e.g. with the
@typeclass command.

"""
#from ev import Character as DefaultCharacter
from game.gamesrc.objects.object import Object
from django.conf import settings

class Character(Object):
    """
    This is just like the Object except it implements its own
    version of the at_object_creation to set up the script
    that adds the default cmdset to the object.
    """

    def basetype_setup(self):
        """
        Setup character-specific security

        You should normally not need to overload this, but if you do, make
        sure to reproduce at least the two last commands in this method (unless
        you want to fundamentally change how a Character object works).

        """
        super(Character, self).basetype_setup()
        self.locks.add(";".join(["get:false()",  # noone can pick up the character
                                 "call:false()"])) # no commands can be called on character from outside
        # add the default cmdset
        self.cmdset.add_default(settings.CMDSET_CHARACTER, permanent=True)

    def at_object_creation(self):
        #self.db.strength = 100
        #self.db.speed = 100
        #self.db.precision = 100
        #self.db.stamina = 100
        
        #self.db.intelligence = 100
        #self.db.charisma = 100
        #self.db.willpower = 100
        #self.db.natural_armor = 0
        pass

    @property
    def name(self):
        return "{Y" + self.key + "{n"
    
    @property
    def name_upper(self):
        return "{Y" + self.key[0].upper() + self.key[1:] + "{n"
    
    #def at_after_move(self, source_location):
    #    "Default is to look around after a move."
    #    self.execute_cmd('look')

    def at_pre_puppet(self, player, sessid=None):
        if self.tags.get("hide_on_unpuppet"):
            """
            This recovers the character again after having been "stoved away"
            at the unpuppet
            """
            if self.db.prelogout_location:
                # try to recover
                self.location = self.db.prelogout_location
            if self.location is None:
                # make sure location is never None (home should always exist)
                self.location = self.home
            if self.location:
                # save location again to be sure
                self.db.prelogout_location = self.location
                self.location.msg_contents("%s has entered the game." % self.name, exclude=[self])
                self.location.at_object_receive(self, self.location)
            else:
                player.msg("{r%s has no location and no home is set.{n" % self, sessid=sessid)

    def at_post_puppet(self):
        self.msg("\nYou become %s.\n" % self.name)
        
        if self.tags.get("hide_on_unpuppet"):
            """
            Called just after puppeting has completed.
            """
            self.execute_cmd("look")
            if self.location:
                self.location.msg_contents("%s has entered the game." % self.name, exclude=[self])

    def at_post_unpuppet(self, player, sessid=None):
        if self.tags.get("hide_on_unpuppet"):
            """
            We stove away the character when the player goes ooc/logs off,
            otherwise the character object will remain in the room also after the
            player logged off ("headless", so to say).
            """
            if self.location: # have to check, in case of multiple connections closing
                self.location.msg_contents("%s has left the game." % self.name, exclude=[self])
                self.db.prelogout_location = self.location
                self.location = None
