# -*- coding: utf-8 -*-
from src.commands.default.muxcommand import MuxCommand

class CmdDefaultExits(MuxCommand):
    locks = "cmd:all()"
    auto_help = False
    
    def func(self):
        "implements the command."
        self.caller.msg("You cannot move in that direction.")

class CmdNorth(CmdDefaultExits):
    key = "north"
    aliases = ["n"]

class CmdNortheast(CmdDefaultExits):
    key = "northeast"
    aliases = ["ne"]
    
class CmdEast(CmdDefaultExits):
    key = "east"
    aliases = ["e"]

class CmdSoutheast(CmdDefaultExits):
    key = "southeast"
    aliases = ["se"]

class CmdSouth(CmdDefaultExits):
    key = "south"
    aliases = ["s"]

class CmdSouthwest(CmdDefaultExits):
    key = "southwest"
    aliases = ["sw"]

class CmdWest(CmdDefaultExits):
    key = "west"
    aliases = ["w"]

class CmdNorthwest(CmdDefaultExits):
    key = "northwest"
    aliases = ["nw"]

class CmdUp(CmdDefaultExits):
    key = "up"
    aliases = ["u"]

class CmdDown(CmdDefaultExits):
    key = "down"
    aliases = ["d"]
