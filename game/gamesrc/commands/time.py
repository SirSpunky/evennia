# -*- coding: utf-8 -*-
from django.conf import settings
import ev
from src.utils import utils, prettytable
from src.commands.default.muxcommand import MuxCommand
import datetime


class CmdTime(MuxCommand):
    """
    time

    Usage:
      time

    Shows the current time of the world, if you can see the sky. Also shows the date.
    """
    key = "time"
    aliases = ["t","date","day","season","week","month","year"]
    locks = "cmd:all()"

    def func(self):
        script_key = "GlobalTime"
        caller = self.caller

        script = ev.search_script(script_key)      
        if not script:
            self.caller.msg("Global script by name '%s' could not be found." % script_key)
            return
        script = script[0] # all ev.search_* methods always return lists
        
        time = script.db.time
        day = script.db.day
        week = script.db.week
        year = script.db.year
        year_name = script.db.year_name
        weeks_per_year = script.db.weeks_per_year

        time_string = ""
        if not caller.location.tags.get("outdoors"):
            time_string = "You cannot see the sky from here."
        else:
        
            if datetime.time(4, 0) <= time < datetime.time(5, 0):
                time_string = "The first light of dawn is hanging in the air."
            elif datetime.time(5, 0) <= time < datetime.time(6, 0):
                time_string = "The twilight of dawn lights up the sky. The sun will soon rise."
            elif datetime.time(6, 0) <= time < datetime.time(6, 30):
                time_string = "The sun has just appeared above the horizon. The sky is red."
            elif datetime.time(6, 30) <= time < datetime.time(7, 00):
                time_string = "The sun is rising. The sky is sparkling with colors."
            elif datetime.time(7, 00) <= time < datetime.time(8, 00):
                time_string = "It's early morning. The sun is still low."
            elif datetime.time(8, 00) <= time < datetime.time(9, 00):
                time_string = "It's morning."
            elif datetime.time(9, 00) <= time < datetime.time(10, 00):
                time_string = "It's late morning. The brightness of day is taking over."
            elif datetime.time(10, 00) <= time < datetime.time(12, 00):
                time_string = "It's forenoon, approaching midday. The sun is climbing high."
            elif datetime.time(12, 00) <= time < datetime.time(13, 00):
                time_string = "It's midday. The sun is right above you."
            elif datetime.time(13, 00) <= time < datetime.time(14, 00):
                time_string = "It's early afternoon. The sun is leaving zenith."
            elif datetime.time(14, 00) <= time < datetime.time(15, 00):
                time_string = "It's late afternoon. The sun is half-way to the horizon."
            elif datetime.time(15, 00) <= time < datetime.time(16, 00):
                time_string = "It's early evening. The sun is approaching the horizon."
            elif datetime.time(16, 00) <= time < datetime.time(17, 00):
                time_string = "It's late evening. The sun is soon setting."
            elif datetime.time(17, 00) <= time < datetime.time(17, 30):
                time_string = "Sunset has begun. Orange colors are lighting up the sky."
            elif datetime.time(17, 30) <= time < datetime.time(18, 00):
                time_string = "The sun has almost disappeared. The sky is burning red."
            elif datetime.time(18, 00) <= time < datetime.time(19, 00):
                time_string = "The sun has just set. Purple colors of dusk are glowing in the sky."
            elif datetime.time(19, 00) <= time < datetime.time(20, 00):
                time_string = "The last light is leaving the sky, giving way to night."
            elif datetime.time(20, 00) <= time < datetime.time(21, 00):
                time_string = "The night has just begun."
            elif datetime.time(21, 00) <= time < datetime.time(23, 00):
                time_string = "The night is growing darker."
            elif datetime.time(23, 00) <= time <= datetime.time(23, 59):
                time_string = "It's right before midnight. The darkness is reaching its peak"
            elif datetime.time(00, 00) <= time < datetime.time(01, 00):
                time_string = "It's the middle of the night. The darkness is overwhelming."
            elif datetime.time(01, 00) <= time < datetime.time(02, 00):
                time_string = "It's past midnight."
            elif datetime.time(02, 00) <= time < datetime.time(03, 00):
                time_string = "It's late night. The darkness is getting lighter."
            elif datetime.time(03, 00) <= time < datetime.time(04, 00):
                time_string = "The night is soon over. The darkness is struggeling."
            
            #time_string += " The time is %s. " % time.strftime("%H:%M")

        if day == 1:
            day_name = "Monday"
        elif day == 2:
            day_name = "Tuesday"
        elif day == 3:
            day_name = "Wednesday"
        elif day == 4:
            day_name = "Thursday"
        elif day == 5:
            day_name = "Friday"
        elif day == 6:
            day_name = "Saturday"
        elif day == 7:
            day_name = "Sunday"
            
        date_string = "%s, Week %s of %s, Year of the %s." % (day_name, week, weeks_per_year, year_name)

        caller.msg(time_string + "\n" + date_string)
        