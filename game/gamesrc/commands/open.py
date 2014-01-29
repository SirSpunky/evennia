# -*- coding: utf-8 -*-
from django.conf import settings
from src.utils import utils, prettytable
from src.commands.default.muxcommand import MuxCommand


class CmdOpen(MuxCommand):
    """
    open

    Usage:
      open <obj>

    Opens an exit or object that is currently closed.
    """
    key = "open"
    locks = "cmd:all()"

    def func(self):
        from game.gamesrc.objects.exit import Exit
        
        caller = self.caller
        location = caller.location
        target = self.lhs

        if not target:
            caller.msg("Open what?")
            return

        obj = caller.search(target, location=[caller, caller.location])
        if not obj:
            return #caller.msg("You can't find %s." % self.rhs)

        if not obj.can_open:
            caller.msg("That cannot be opened.")
            return
        if obj.is_open:
            caller.msg("It's already open.")
            return
        
        obj.open(caller)
        
        if isinstance(obj, Exit):
            caller.msg("You open the entrance leading %s." % obj.name)
            caller.location.msg_contents("%s opens the entrance leading %s." % (caller.name, obj.name), exclude=caller)
            obj.get_opposite_exit().location.msg_contents("The entrance leading %s opens from the other side." % (obj.get_opposite_exit().name))
        else:
            caller.msg("You open %s." % obj.name)
            caller.location.msg_contents("%s opens %s." % (caller.name, obj.name), exclude=caller)

        # calling hook method
        #obj.at_open(caller)