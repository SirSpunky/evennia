# -*- coding: utf-8 -*-
from django.conf import settings
from src.utils import utils, prettytable
from src.commands.default.muxcommand import MuxCommand

class CmdAttack(MuxCommand):
    """
    attack

    Usage:
      attack <target>
      attack stop

    Attack a target. Use "attack stop" to stop attacking.
    """

    key = "attack"
    aliases = ["a", "hit", "h", "kill", "k"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        target = self.lhs
        
        if not target:
            caller.msg("Attack whom?")
            return

        if target == "stop":
            caller.msg("You stop attacking.")
            return
        
        
        target_obj = caller.search(target, location=caller.location)
        
        if not target_obj:
            caller.msg("Could not find '%s'." % target)
            return
        
        

        #caller.msg('You attack %s!' % (target_obj.name))
        
        #target_obj.msg('%s attacks you!' % (target_obj.name_upper))
        
        caller.attack(target_obj)
        
        #target_obj.attack(caller)
        
        #target_obj.at_sayto(caller, speech)
