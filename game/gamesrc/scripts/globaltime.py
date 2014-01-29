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

class GlobalTime(Script):
    """
    This class defines the script itself

Remove and add script:
@py ev.search_script("GlobalTime")[0].stop(kill=True)
@py ev.create_script("game.gamesrc.scripts.globaltime.GlobalTime")
    """
    def at_script_creation(self):
        # Default variables
        self.key = self.__class__.__name__ #"repeatmessage"
        self.desc = "Adds global time."
        self.interval = 60 # In seconds. Should represent 15 minutes in game.
        self.repeats = 0  # repeat only a certain number of times. 0 = infinte
        self.start_delay = True  # wait self.interval until first call
        self.persistent = True

        # Custom variables
        self.db.time = datetime.time(6, 0) # Current time, hours and minutes
        self.db.day = 1
        self.db.week = 1
        self.db.year = 1
        self.db.weeks_per_year = 16
        self.db.year_names = ['Goat', 'Three-Headed Monkey', 'Seven Moons', 'Worm', 'Pig', 'Dolphin', 'Three Suns', 'Happy Farmer', 'Lute', 'Snake', 'Elephant King', 'Leopard God']
        self.db.year_name = 'Goat'
        self.db.used_year_names = []

    def at_repeat(self):
        """
        This gets called every self.interval seconds.
        """
        
        fulldate = datetime.datetime(100, 1, 1, self.db.time.hour, self.db.time.minute, self.db.time.second) # Must convert to full date to be able to use datetime.timedelta
        fulldate = fulldate + datetime.timedelta(minutes=15)
        time = fulldate.time()
        self.db.time = time
        
        # TODO: If past midnight, increase day, week, year
        if time == datetime.time(0, 0):
            self.db.day += 1
        
        if self.db.day > 7:
            self.db.week += 1
            self.db.day = 1
        
        if self.db.week > self.db.weeks_per_year:
            self.db.year += 1
            self.db.week = 1
            
            # Pick a random new year name that has not been used before. 
            if len(self.db.used_year_names) == len(self.db.year_names) - 1: # If all names have been used up, reset names.
                self.db.used_year_names = []
            
            # Add year name to used names
            self.db.used_year_names.append(self.db.year_name)
            
            # Create a temp list of valid names, excluding used names
            valid_year_names = self.db.year_names
            for name in self.db.used_year_names:
                valid_year_names.remove(name)
            
            # Find random year name from valid names
            from random import choice
            self.db.year_name = choice(valid_year_names)
        
        msg = ""
        
        if time == datetime.time(0, 0):
            msg = "The darkness has reached its peak. It's midnight."
        if time == datetime.time(4, 0):
            msg = "The first light of dawn is hanging in the air."
        if time == datetime.time(6, 0):
            msg = "The sun is rising."
        if time == datetime.time(12, 0):
            msg = "The sun has reached zenith. It's midday."
        if time == datetime.time(16, 0):
            msg = "It's getting darker outside."        
        if time == datetime.time(18, 0):
            msg = "The sun disappears over the horizon."
        if time == datetime.time(20, 0):
            msg = "The last light of day is gone. The night has begun."

        if msg:
            rooms = ev.search_tag("outdoors")
            for room in rooms:
                room.msg_contents(msg)

