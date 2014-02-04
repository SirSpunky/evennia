# -*- coding: utf-8 -*-
from django.conf import settings
from src.utils import utils, prettytable
from src.commands.default.muxcommand import MuxCommand


class CmdGet(MuxCommand):
    """
    get

    Usage:
      get <obj>

    Picks up an object from your location and puts it in
    your inventory.
    """
    key = "get"
    locks = "cmd:all()"

    def func(self):
        "implements the command."

        caller = self.caller
        to_get = self.lhs

        if not to_get:
            caller.msg("Get what?")
            return
        #print "general/get:", caller, caller.location, self.args, caller.location.contents
        
        if self.rhs:
            location_name = self.rhs
        else:
            to_get = None
            location_name = None
            if self.lhs:
                to_get = self.lhs.split(' ', 1)[0]
                if len(self.lhs.split(' ', 1)) > 1:
                    location_name = self.lhs.split(' ', 1)[1]
        
        if location_name:            
            location = caller.search(location_name, location=[caller, caller.location])
            
            if not location:
                caller.msg("You can't find %s." % location_name)
                return
        else:
            location = caller.location

        obj = caller.search(to_get, location=location)
        if not obj:
            return

        if obj == caller:
            caller.msg("You can't pick up yourself.")
            return
        #print obj, obj.location, caller, caller==obj.location
        if obj.location == caller:
            caller.msg("You already carry that.")
            return
        if obj.own_weight == 0:
            caller.msg("You cannot pick that up.")
            return
        if obj.total_weight > caller.max_pickup_weight:
            caller.msg("That is too heavy for you.")
            return
        if obj.total_weight + caller.contents_weight > caller.max_contents_weight:
            caller.msg("It won't fit in your inventory.")
            return
        
        
        #if not obj.access(caller, 'get'):
        #    if obj.db.get_err_msg:
        #        caller.msg(obj.db.get_err_msg)
        #    else:
        #        caller.msg("You can't pick that up.")
        #    return

        obj.move_to(caller, quiet=True)
        
        if location == caller.location:
            caller.msg("You pick up %s." % obj.name)
            caller.location.msg_contents("%s picks up %s." % (caller.name, obj.name), exclude=caller)
        else:
            caller.msg("You take out %s from %s." % (obj.name, location.name))
            caller.location.msg_contents("%s takes out %s from %s." % (caller.name, obj.name, location.name), exclude=caller)

        
        # calling hook method
        obj.at_get(caller)