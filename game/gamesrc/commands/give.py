# -*- coding: utf-8 -*-
from django.conf import settings
from src.utils import utils, prettytable
from src.commands.default.muxcommand import MuxCommand


class CmdGive(MuxCommand):
    """
    give away things

    Usage:
      give <inventory obj> = <target>

    Gives an items from your inventory to another character,
    placing it in their inventory.
    """
    key = "give"
    aliases = ["put"]
    locks = "cmd:all()"

    def func(self):
        "Implement give"
        from game.gamesrc.objects.character import Character

        caller = self.caller
        if not self.args:
            caller.msg("Usage: give/put <inventory object> = <target>")
            return
        
        # Parse input
        
        
        if self.rhs:
            to_give_name = self.lhs
            target_name = self.rhs
        else:
            to_give_name = None
            target_name = None
            if self.lhs:
                to_give_name = self.lhs.split(' ', 1)[0]
                if len(self.lhs.split(' ', 1)) > 1:
                    target_name = self.lhs.split(' ', 1)[1]
            
            if not target_name:
                return
        
        to_give = caller.search(to_give_name, location=caller)
        target = caller.search(target_name)
        if not (to_give and target):
            return
        if target == caller:
            caller.msg("You keep %s to yourself." % to_give.name)
            return
        #if not to_give.location == caller:
        #    caller.msg("You are not holding %s." % to_give.name)
        #    return
        # give object
        
        
        if isinstance(target, Character):
            if to_give.total_weight + target.contents_weight > target.max_contents_weight:
                caller.msg("%s cannot carry %s." % (target.name, to_give.name))
                return
            
            to_give.location = target
            caller.msg("You give %s to %s." % (to_give.name, target.name))
            target.msg("%s gives you %s." % (caller.name, to_give.name))
            caller.location.msg_contents("%s gives %s to %s." % (caller.name, to_give.name, target.name), exclude=[caller, target])
        else:
            if not target.is_container:
                caller.msg("That's not a container.")
                return
            if to_give.total_weight + target.contents_weight > target.max_contents_weight:
                caller.msg("It's full.")
                return

            to_give.location = target
            caller.msg("You put %s in %s." % (to_give.name, target.name))
            target.msg("%s puts %s in you." % (caller.name, to_give.name))
            caller.location.msg_contents("%s puts %s in %s." % (caller.name, to_give.name, target.name), exclude=[caller, target])
