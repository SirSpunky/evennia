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
from game.gamesrc.objects.exit import Exit
from game.gamesrc.objects.character import Character

class RandomMessage(Script):
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

        if self.obj.db.random_message_rate:
            if random.random() < 1.0 - self.obj.db.random_message_rate:
                # No message this time
                return
        
        # Return a random message
        rand = random.random()
        messages = self.obj.db.random_messages
        
        if len(messages) > 0:
            chance_per_message = 1.0/len(messages)
            
            i = 0
            for msg in messages:
                i += 1
                if rand <= i*chance_per_message:
                    # $random_character is replaced with random character in room, excluding caller, if one is available.
                    if msg.find('$random_character') != -1:
                        chars = []
                        for obj in self.obj.location.contents:
                            if isinstance(obj, Character) and obj != self.obj:
                                chars.append(obj)
                        if len(chars) == 0:
                            return # If no chars were found, skip message.
                        r = int(random.random() * len(chars))
                        random_char = chars[r]
                        msg = msg.replace("$random_character", random_char.name);
                    
                    # Prefix string with "/" to execute command instead of displaying message.
                    if msg[0] == "/":
                        self.obj.execute_cmd(msg[1:])
                    else:
                        if self.obj.location:
                            self.obj.location.msg_contents(msg)
                        else:
                            self.obj.msg_contents(msg)
                    return
