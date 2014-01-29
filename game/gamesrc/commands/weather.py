# -*- coding: utf-8 -*-
from django.conf import settings
import ev
from src.utils import utils, prettytable
from src.commands.default.muxcommand import MuxCommand
import datetime


class CmdWeather(MuxCommand):
    """
    weather

    Usage:
      weather

    Shows the current time of the world, if you can see the sky. Also shows the date.
    """
    key = "weather"
    aliases = ["sky","clouds","temperature","wind","rain"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller

        # Get weather data
        script_key = "GlobalWeather"
        script = ev.search_script(script_key)      
        if not script:
            self.caller.msg("Global script by name '%s' could not be found." % script_key)
            return
        script = script[0] # all ev.search_* methods always return lists
        
        if not caller.location.tags.get("outdoors"):
            self.caller.msg("You cannot see the weather from here.")
            return
        
        cloud_density = script.db.cloud_density
        wind_speed = script.db.wind_speed
        precipitation_level = script.db.precipitation_level
        precipitation_type = script.db.precipitation_type
        
        # Get time data
        script_key = "GlobalTime"
        script = ev.search_script(script_key)      
        if not script:
            self.caller.msg("Global script by name '%s' could not be found." % script_key)
            return
        script = script[0] # all ev.search_* methods always return lists
        
        time = script.db.time
        
        # Generate weather string
        if cloud_density == 0:
            cloud_string = "The sky is clear."
        elif cloud_density == 1:
            cloud_string = "A few small clouds are hanging in the sky."
        elif cloud_density == 2:
            cloud_string = "Light clouds are scattered across the sky."
        elif cloud_density == 3:
            cloud_string = "The sky is partly cloudy."
        elif cloud_density == 4:
            cloud_string = "The sky is covered with clouds."
        elif cloud_density == 5:
            cloud_string = "Dark clouds cover the sky."
        elif cloud_density == 6:
            cloud_string = "Black clouds stretches across the sky."
        elif cloud_density == 7:
            cloud_string = "Huge, black pillars of cloud reaches high up in the atmosphere."
        
        if wind_speed == 0:
            wind_string = "It's nearly windless."
        elif wind_speed == 1:
            wind_string = "The wind is calm."
        elif wind_speed == 2:
            wind_string = "A gentle breeze is stirring the air."
        elif wind_speed == 3:
            wind_string = "There's a strong breeze in the air."
        elif wind_speed == 4:
            wind_string = "A gale is blowing. The wind speeds are strong."
        elif wind_speed == 5:
            wind_string = "Storm winds are raging."
        elif wind_speed == 6:
            wind_string = "Violent storm winds are howling in the air."
        elif wind_speed == 7:
            wind_string = "There's a hurricane. The wind strength is incredible."
        
        string = "%s %s" % (cloud_string, wind_string)

        msg = ""
        if precipitation_level == 1:
            if precipitation_type == "rain":
                msg = "It's raining a little."
                if cloud_density < 4 and datetime.time(6, 30) <= time < datetime.time(9, 0):
                    msg += " A beautiful rainbow arcs across the sky."
                if cloud_density < 4 and datetime.time(14, 00) <= time < datetime.time(17, 30):
                    msg += " A beautiful rainbow arcs across the sky."
            elif precipitation_type == "snow":
                msg = "It's snowing a little."
            elif precipitation_type == "hail":
                msg = "It's hailing a little."
        
        if precipitation_level == 2:
            if precipitation_type == "rain":
                msg = "It's raining."
            elif precipitation_type == "snow":
                msg = "It's snowing."
            elif precipitation_type == "hail":
                msg = "It's hailing."
        
        if precipitation_level == 3:
            if precipitation_type == "rain":
                msg = "It's raining a lot."
            elif precipitation_type == "snow":
                msg = "It's snowing a lot."
            elif precipitation_type == "hail":
                msg = "It's hailing a lot."
        
        if precipitation_level == 4:
            if precipitation_type == "rain":
                msg = "Rain is pouring down."
            elif precipitation_type == "snow":
                msg = "Massive amounts of snow are falling."
            elif precipitation_type == "hail":
                msg = "Massive amounts of hail are falling."
        
        if msg:
            string += "\n%s" % msg

        caller.msg(string)
        