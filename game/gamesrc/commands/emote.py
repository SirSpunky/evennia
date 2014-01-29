# -*- coding: utf-8 -*-
from django.conf import settings
from src.utils import utils, prettytable
from src.commands.default.muxcommand import MuxCommand



class CmdEmote(MuxCommand):
    """
    me - Describe a custom action.

    Usage:
      me <emote text>
      me's <emote text>

    Example:
      me is standing by the wall, smiling.
       -> others will see:
      Tom is standing by the wall, smiling.

    Describe an action being taken. The emote text will
    automatically begin with your name.
    """
    key = "me"
    aliases = ["emote", "pose", ":"]
    locks = "cmd:all()"

    def parse(self):
        """
        Custom parse the cases where the emote
        starts with some special letter, such
        as 's, at which we don't want to separate
        the caller's name and the emote with a
        space.
        """
        args = self.args
        if args and not args[0] in ["'", ",", ":"]:
            args = " %s" % args.strip()
        self.args = args

    def func(self):
        "Hook function"
        if not self.args:
            msg = "What do you want to do?"
            self.caller.msg(msg)
        else:
            msg = "%s%s" % (self.caller.name_upper, self.args)
            
            # Add period after sentence.
            chars = ",.!?"
            if msg[-1:] not in chars:
                msg += "."
                
            self.caller.location.msg_contents(msg)