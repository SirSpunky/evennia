"""
Example script for testing. This adds a simple timer that
has your character make observations and noices at irregular
intervals.

To test, use
  @script me = examples.bodyfunctions.BodyFunctions

The script will only send messages to the object it
is stored on, so make sure to put it on yourself
or you won't see any messages!

"""
import random
import ev
from ev import Script
import datetime

class GlobalDatabase(Script):
    """
    This class defines the script itself

Remove and add script:
@py ev.search_script("GlobalDatabase")[0].stop(kill=True)
@py ev.create_script("game.gamesrc.scripts.globaldatabase.GlobalDatabase")
    """
    def at_script_creation(self):
        # Default variables
        self.key = self.__class__.__name__ #"repeatmessage"
        self.desc = "Global database. DO NOT DELETE."
        self.interval = 0 # In seconds. Should represent 15 minutes in game.
        self.repeats = 0  # repeat only a certain number of times. 0 = infinte
        self.start_delay = True  # wait self.interval until first call
        self.persistent = True

        # Custom variables
        self.db.database = {}

    def at_repeat(self):
        """
        This gets called every self.interval seconds.
        """
        
        pass

