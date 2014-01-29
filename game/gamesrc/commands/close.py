# -*- coding: utf-8 -*-
from django.conf import settings
from src.utils import utils, prettytable
from src.commands.default.muxcommand import MuxCommand


class CmdClose(MuxCommand):
    """
    close

    Usage:
      close <obj>

    Closes an exit or object that is currently closed.
    """
    key = "close"
    locks = "cmd:all()"

    def func(self):
        from game.gamesrc.objects.exit import Exit
        
        caller = self.caller
        location = caller.location
        target = self.lhs

        if not target:
            caller.msg("Close what?")
            return

        obj = caller.search(target, location=[caller, caller.location])
        if not obj:
            return #caller.msg("You can't find %s." % self.rhs)

        if not obj.can_open:
            caller.msg("That cannot be closed.")
            return
        if not obj.is_open:
            caller.msg("It's already closed.")
            return
        
        obj.close(caller)
        
        if isinstance(obj, Exit):
            caller.msg("You close the entrance leading %s." % obj.name)
            caller.location.msg_contents("%s closes the entrance leading %s." % (caller.name, obj.name), exclude=caller)
            obj.get_opposite_exit().location.msg_contents("The entrance leading %s closes from the other side." % (obj.get_opposite_exit().name))
        else:
            caller.msg("You close %s." % obj.name)
            caller.location.msg_contents("%s closes %s." % (caller.name, obj.name), exclude=caller)

        # calling hook method
        #obj.at_close(caller)