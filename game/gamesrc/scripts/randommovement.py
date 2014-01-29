# -*- coding: utf-8 -*-
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
from ev import Script

class RandomMovement(Script):
    """
    This class defines the script itself
    """
    def at_script_creation(self):
        # Default variables
        self.key = self.__class__.__name__ #"repeatmessage"
        self.desc = "Adds various timed events to an object."
        self.interval = 10
        self.repeats = 0  # repeat only a certain number of times. 0 = infinte
        self.start_delay = True  # wait self.interval until first call
        self.persistent = True
        

    def at_repeat(self):
        """
        This gets called every self.interval seconds.
        """


        if self.obj.db.random_movement_rate:
            if random.random() < 1.0 - self.obj.db.random_movement_rate:
                # No message this time
                return
        
        # Move to a random exit
        from game.gamesrc.objects.exit import Exit
        
        if self.obj.location:
            valid_exits = []
            for obj in self.obj.location.contents:
                if isinstance(obj, Exit):
                    if obj.is_open:
                        valid_exits.append(obj)
            
            if len(valid_exits) > 0:
                rand = int(random.random() * len(valid_exits))
                self.obj.move_to(valid_exits[rand].destination)
                
