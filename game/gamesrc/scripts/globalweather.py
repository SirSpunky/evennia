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

class GlobalWeather(Script):
    """
    This class defines the script itself

Remove and add global script:
@py ev.search_script("GlobalWeather")[0].stop(kill=True)
@py ev.create_script("game.gamesrc.scripts.globalweather.GlobalWeather")
    """
    def at_script_creation(self):
        # Default variables
        self.key = self.__class__.__name__ #"repeatmessage"
        self.desc = "Adds global weather."
        self.interval = 10 # In seconds.
        self.repeats = 0  # repeat only a certain number of times. 0 = infinte
        self.start_delay = True  # wait self.interval until first call
        self.persistent = True

        # Custom variables
        self.db.cloud_density = 0 # Current cloud density, 0-7
        self.db.wind_speed = 0 # Current wind speed, 0-7
        self.db.precipitation_level = 0 # Current precipitation level, 0-4
        self.db.precipitation_type = "rain" # Current precipitation type: rain, snow or hail
        
        self.db.cloud_change_rate = 0.2 # The higher it is, changes will happen more often.
        self.db.cloud_increase_rate = 1 # The higher it is, increases in strength will happen more often.
        self.db.wind_change_rate = 0.2 # The higher it is, changes will happen more often.
        self.db.wind_increase_rate = 1 # The higher it is, increases in strength will happen more often.
        self.db.precipitation_change_rate = 0.5 # The higher it is, changes will happen more often.
        self.db.precipitation_increase_rate = 0 # The higher it is, increases in strength will happen more often. Set automatically depending on cloud density.
        self.db.precipitation_msg_timer = 0 # An automatic timer constantly ticking up.

    def at_repeat(self):
        """
        This gets called every self.interval seconds.
        """
        
        msg = ""
        
        
        # Precipitation - Messages
        self.db.precipitation_msg_timer += self.interval
        
        if self.db.precipitation_level == 1 and self.db.precipitation_msg_timer >= 50:
            self.db.precipitation_msg_timer = 0
            if self.db.precipitation_type == "rain":
                msg = "Light rain is falling from the sky."
            elif self.db.precipitation_type == "snow":
                msg = "Small snowflakes are falling from the sky."
            elif self.db.precipitation_type == "hail":
                msg = "Small hailstones are falling from the sky."
        
        if self.db.precipitation_level == 2 and self.db.precipitation_msg_timer >= 30:
            self.db.precipitation_msg_timer = 0
            if self.db.precipitation_type == "rain":
                msg = "Rain is falling from the sky."
            elif self.db.precipitation_type == "snow":
                msg = "Snow is falling from the sky."
            elif self.db.precipitation_type == "hail":
                msg = "Hail is falling from the sky."
        
        if self.db.precipitation_level == 3 and self.db.precipitation_msg_timer >= 20:
            self.db.precipitation_msg_timer = 0
            if self.db.precipitation_type == "rain":
                msg = "Heavy rain is pouring down."
            elif self.db.precipitation_type == "snow":
                msg = "Large snowflakes are falling."
            elif self.db.precipitation_type == "hail":
                msg = "Large hailstones are hammering on the ground."
        
        if self.db.precipitation_level == 4 and self.db.precipitation_msg_timer >= 10:
            self.db.precipitation_msg_timer = 0
            if self.db.precipitation_type == "rain":
                msg = "Massive amounts of rain are pouring down."
            elif self.db.precipitation_type == "snow":
                msg = "Massive amounts of snow are falling."
            elif self.db.precipitation_type == "hail":
                msg = "Huge hailstones are crushing down from the skies."
        
        
        
        # Cloud density
        if random.random() < 0.025 * self.db.cloud_change_rate:
            # Only small chance of changing
            
            # Clear sky
            if self.db.cloud_density == 0:
                if random.random() < 0.5 * self.db.cloud_increase_rate:
                    self.db.cloud_density += 1
            
            # Few clouds
            elif self.db.cloud_density == 1:
                if random.random() < 0.5 * self.db.cloud_increase_rate:
                    self.db.cloud_density += 1
                    self.db.precipitation_increase_rate = 0.5
                else:
                    self.db.cloud_density -= 1
            
            # Light clouds
            elif self.db.cloud_density == 2:
                if random.random() < 0.5 * self.db.cloud_increase_rate:
                    self.db.cloud_density += 1
                    self.db.precipitation_increase_rate = 0.75
                else:
                    self.db.cloud_density -= 1
                    self.db.precipitation_increase_rate = 0
            
            # Partly cloudy
            elif self.db.cloud_density == 3:
                if random.random() < 0.3 * self.db.cloud_increase_rate:
                    self.db.cloud_density += 1
                    self.db.wind_increase_rate *= 1.5
                    self.db.precipitation_increase_rate = 1
                else:
                    self.db.cloud_density -= 1
                    self.db.precipitation_increase_rate = 0.5
            
            # Cloud covered
            elif self.db.cloud_density == 4:
                if random.random() < 0.2 * self.db.cloud_increase_rate:
                    self.db.cloud_density += 1
                    self.db.precipitation_increase_rate = 2
                    msg = "The clouds are darkening."
                else:
                    self.db.cloud_density -= 1
                    self.db.wind_increase_rate /= 1.5
                    self.db.precipitation_increase_rate = 0.75
            
            # Dark cloud covered
            elif self.db.cloud_density == 5:
                if random.random() < 0.3 * self.db.cloud_increase_rate:
                    self.db.cloud_density += 1
                    self.db.wind_increase_rate *= 1.5
                    self.db.precipitation_increase_rate = 2.5
                    msg = "The clouds are turning black. Everything is getting darker."
                else:
                    self.db.cloud_density -= 1
                    self.db.precipitation_increase_rate = 1
                    msg = "The clouds are lightening up."
            
            # Black clouds
            elif self.db.cloud_density == 6:
                if random.random() < 0.1 * self.db.cloud_increase_rate:
                    self.db.cloud_density += 1
                    self.db.wind_increase_rate *= 1.5
                    msg = "The clouds are turning into black, anvil-shaped monsters."
                else:
                    self.db.cloud_density -= 1
                    self.db.wind_increase_rate /= 1.5
                    self.db.precipitation_increase_rate = 2
                    msg = "The clouds are lightening up."
            
            # Black pillars
            elif self.db.cloud_density == 7:
                if random.random() < 0.4 * self.db.cloud_increase_rate:
                    pass
                else:
                    self.db.cloud_density -= 1
                    self.db.wind_increase_rate /= 1.5
                    msg = "The most threatening clouds are disappearing."
        
        
        
        # Wind speed
        if random.random() < 0.025 * self.db.wind_change_rate: # Every 5th minute
            # Only small chance of changing
            
            # Windless
            if self.db.wind_speed == 0:
                if random.random() < 0.75 * self.db.wind_increase_rate:
                    self.db.wind_speed += 1
            
            # Calm
            elif self.db.wind_speed == 1:
                if random.random() < 0.5 * self.db.wind_increase_rate:
                    self.db.wind_speed += 1
                else:
                    self.db.wind_speed -= 1
            
            # Gentle breeze
            elif self.db.wind_speed == 2:
                if random.random() < 0.35 * self.db.wind_increase_rate:
                    self.db.wind_speed += 1
                else:
                    self.db.wind_speed -= 1
            
            # Strong breeze
            elif self.db.wind_speed == 3:
                if random.random() < 0.25 * self.db.wind_increase_rate:
                    self.db.wind_speed += 1
                    msg = "The wind is getting stronger."
                else:
                    self.db.wind_speed -= 1
            
            # Gale
            elif self.db.wind_speed == 4:
                if random.random() < 0.1 * self.db.wind_increase_rate:
                    self.db.wind_speed += 1
                    msg = "The wind has reached storm strength."
                else:
                    self.db.wind_speed -= 1
            
            # Storm
            elif self.db.wind_speed == 5:
                if random.random() < 0.1 * self.db.wind_increase_rate:
                    self.db.wind_speed += 1
                    msg = "The wind is extremely strong, surpassing a normal storm."
                else:
                    self.db.wind_speed -= 1
                    msg = "The wind is weakening. It's no longer storm strength."
            
            # Violent storm
            elif self.db.wind_speed == 6:
                if random.random() < 0.05 * self.db.wind_increase_rate:
                    self.db.wind_speed += 1
                    msg = "Hurricane winds are ripping through the air."
                else:
                    self.db.wind_speed -= 1
                    msg = "The wind is weakening, but remains storm strength."
            
            # Hurricane
            elif self.db.wind_speed == 7:
                if random.random() < 0.25 * self.db.wind_increase_rate:
                    pass
                else:
                    self.db.wind_speed -= 1
                    msg = "The wind is weakening, but is still violent."
        
        
        
        # Precipitation
        if random.random() < 0.025 * self.db.precipitation_change_rate: # Every 5th minute            
            if self.db.precipitation_level == 0:
                if random.random() < (0.1 + self.db.wind_speed / 30) * self.db.precipitation_increase_rate:
                    self.db.precipitation_level += 1
            
            elif self.db.precipitation_level == 1:
                if random.random() < 0.2 * self.db.precipitation_increase_rate:
                    self.db.precipitation_level += 1
                elif random.random() < 0.4 * self.db.precipitation_increase_rate:
                    pass
                else:
                    self.db.precipitation_level -= 1
            
            elif self.db.precipitation_level == 2:
                if random.random() < 0.1 * self.db.precipitation_increase_rate:
                    self.db.precipitation_level += 1
                elif random.random() < 0.3 * self.db.precipitation_increase_rate:
                    pass
                else:
                    self.db.precipitation_level -= 1
            
            elif self.db.precipitation_level == 3:
                if random.random() < 0.05 * self.db.precipitation_increase_rate:
                    self.db.precipitation_level += 1
                elif random.random() < 0.15 * self.db.precipitation_increase_rate * self.db.precipitation_increase_rate:
                    pass
                else:
                    self.db.precipitation_level -= 1
            
            elif self.db.precipitation_level == 4:
                if random.random() < 0.15 * self.db.precipitation_increase_rate * self.db.precipitation_increase_rate:
                    pass
                else:
                    self.db.precipitation_level -= 1
            
            
            # Precipitation - Chance to change type
            if self.db.precipitation_type == "rain":
                if self.db.cloud_density >= 4 and self.db.wind_speed >= 4 and random.random() < 0.01:
                    self.db.precipitation_type == "hail"
                elif random.random() < 0.005:
                    self.db.precipitation_type == "snow"
            
            elif self.db.precipitation_type == "snow" and random.random() < 0.01:
                self.db.precipitation_type == "rain"
            
            elif self.db.precipitation_type == "hail" and random.random() < 0.1:
                self.db.precipitation_type == "rain"
            
                
        
        
        # TODO: Tornado. Thunder. Fog.
        #rooms = ev.search_tag("outdoors")

        
        if msg:
            # Send message to active players only.
            from src.server.sessionhandler import SESSIONS
            for s in SESSIONS.get_sessions():
                player_object = s.get_puppet()
                if s.logged_in and player_object and player_object.location.tags.get("outdoors"):
                    player_object.msg(msg)

