# -*- coding: utf-8 -*-
from django.conf import settings
import ev
from src.utils import utils, prettytable
from src.commands.default.muxcommand import MuxCommand
import datetime
from game.gamesrc.utils.get_map import get_map


class CmdMap(MuxCommand):
    """
    map

    Usage:
      map

    Shows a map of your surroundings.
    """
    key = "map"
    aliases = ["m"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        
        if self.lhs == 'all':
            output = get_map(caller, 40, 15, True)
        else:
            output = get_map(caller, 40, 15, False)

        caller.msg(output)
        