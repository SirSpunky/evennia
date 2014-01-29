# -*- coding: utf-8 -*-

import traceback
import os
import datetime
import time
import sys
import django
import twisted
from time import time as timemeasure

import ev
from django.conf import settings
from src.server.caches import get_cache_sizes
from src.server.sessionhandler import SESSIONS
from src.scripts.models import ScriptDB
from src.objects.models import ObjectDB
from src.players.models import PlayerDB
from src.utils import logger, utils, gametime, create, is_pypy, prettytable
from src.utils.utils import crop
from src.commands.default.muxcommand import MuxCommand
from src.utils import utils, prettytable

try:
    # used by @set
    from ast import literal_eval as _LITERAL_EVAL
except ImportError:
    # literal_eval is not available before Python 2.6
    _LITERAL_EVAL = None

class CmdArea(MuxCommand):
    """
    .area - Define areas

    Usage:
        .area add <areakey>              Add new area
        .area delete <areakey>           Delete area
        .area <areakey>                  List all attributes on area
        .area <areakey>/<attr> = <value> Set attribute
        .area <areakey>/<attr>           Inspect attribute
        .area <areakey>/<attr> =         Delete attribute

    Attributes:
        max_rooms            0+. Maximum number of rooms for this area.
        max_exits            1-6. Maximum number of exits for any room in this area.
        tunneling_bias       0.00-1.00. Higher value will build longer tunnels of rooms.
        straightness_bias    -1.00-1.00. Higher value will build rooms along straight lines.
        rooms                {'roomkey': 0.00+, ...}. All valid rooms of this area and their corresponding weights. Higher weight means they'll appear more often. Example: {'cave': 1, 'cavern': 0.1} Room with key 'cave' will appear ten times more often than 'cavern'.
    """

    key = ".area"
    aliases = [".areas"]
    locks = "cmd:perm(create) or perm(Builders)"
    help_category = "Building"

    def convert_from_string(self, strobj):
        """
        Converts a single object in *string form* to its equivalent python
        type.

         Python earlier than 2.6:
        Handles floats, ints, and limited nested lists and dicts
        (can't handle lists in a dict, for example, this is mainly due to
        the complexity of parsing this rather than any technical difficulty -
        if there is a need for @set-ing such complex structures on the
        command line we might consider adding it).
         Python 2.6 and later:
        Supports all Python structures through literal_eval as long as they
        are valid Python syntax. If they are not (such as [test, test2], ie
        withtout the quotes around the strings), the entire structure will
        be converted to a string and a warning will be given.

        We need to convert like this since all data being sent over the
        telnet connection by the Player is text - but we will want to
        store it as the "real" python type so we can do convenient
        comparisons later (e.g.  obj.db.value = 2, if value is stored as a
        string this will always fail).
        """

        def rec_convert(obj):
            """
            Helper function of recursive conversion calls. This is only
            used for Python <=2.5. After that literal_eval is available.
            """
            # simple types
            try:
                return int(obj)
            except ValueError:
                pass
            try:
                return float(obj)
            except ValueError:
                pass
            # iterables
            if obj.startswith('[') and obj.endswith(']'):
                "A list. Traverse recursively."
                return [rec_convert(val) for val in obj[1:-1].split(',')]
            if obj.startswith('(') and obj.endswith(')'):
                "A tuple. Traverse recursively."
                return tuple([rec_convert(val) for val in obj[1:-1].split(',')])
            if obj.startswith('{') and obj.endswith('}') and ':' in obj:
                "A dict. Traverse recursively."
                return dict([(rec_convert(pair.split(":", 1)[0]),
                              rec_convert(pair.split(":", 1)[1]))
                             for pair in obj[1:-1].split(',') if ":" in pair])
            # if nothing matches, return as-is
            return obj

        if _LITERAL_EVAL:
            # Use literal_eval to parse python structure exactly.
            try:
                return _LITERAL_EVAL(strobj)
            except (SyntaxError, ValueError):
                # treat as string
                string = "{RNote: Value was converted to string. If you don't want this, "
                string += "use proper Python syntax, like enclosing strings in quotes.{n"
                self.caller.msg(string)
                return utils.to_str(strobj)
        else:
            # fall back to old recursive solution (does not support
            # nested lists/dicts)
            return rec_convert(strobj.strip())
    
    def func(self):
        
        # Find global script
        script_key = "GlobalDatabase"
        script = ev.search_script(script_key)
        if not script:
            self.caller.msg("Global script by name '%s' could not be found." % script_key)
            return
        script = script[0] # all ev.search_* methods always return lists
        
        # Make sure the dictionary already exists in the global database script.
        if "areas" not in script.db.database:
            script.db.database["areas"] = {}
        
        # Parse input
        self.lhs = self.lhs.lower()
        command = ""
        target = ""
        if self.lhs:
            command = self.lhs.split(' ', 1)[0]
            if len(self.lhs.split(' ', 1)) > 1:
                target = self.lhs.split(' ', 1)[1]
        
        

        
        if command == "":
            # View all areas
        
            table = prettytable.PrettyTable(["Name", "Max rooms"])
            table.header = True
            table.border = False
            for key, area in script.db.database["areas"].iteritems():
                if "maxrooms" in area:
                    maxrooms = area["maxrooms"]
                else:
                    maxrooms = ""
                table.add_row([key, maxrooms])
            
            self.caller.msg("Areas:\n\n%s" % unicode(table))
        elif command == "delete":
            if not target:
                self.caller.msg("Which area do you wish to delete?")
                return
            
            if not target in script.db.database["areas"]:
                self.caller.msg("Cannot find area '%s'." % target)
                return
            
            script.db.database["areas"].pop(target, None)
            
            self.caller.msg("Area '%s' was deleted." % target)
        
        elif command == "add":
            if not target:
                self.caller.msg("You must specify an area key to add.")
                return

            if target in script.db.database["areas"]:
                self.caller.msg("There's already an area with key '%s'." % target)
                return

            area = {}
            
            script.db.database["areas"][target] = area
            
            self.caller.msg("Area '%s' was added." % target)
        
        else:
            lhs_split = self.lhs.split('/')
            areakey = lhs_split[0]
            attr = ""
            if len(lhs_split) > 1:
                attr = lhs_split[1]
            new_value = self.rhs
            
            if not areakey in script.db.database["areas"]:
                self.caller.msg("Cannot find area '%s'." % target)
                return
            
            if attr == "":
                # Attribute not included. List all attributes on area.
                string = ""
                for key, value in script.db.database["areas"][areakey].iteritems():
                    string += "Attribute %s/%s = %s\n" % (areakey, key, value)
                
                self.caller.msg(string, raw=True)
                return
            else:
                if not new_value and not attr in script.db.database["areas"][areakey]:
                    self.caller.msg("No such attribute has been set.")
                    return
                
                if new_value == None:
                    # No right hand side at all. Just display attribute.
                    self.caller.msg("Attribute %s/%s = %s" % (areakey, attr, script.db.database["areas"][areakey][attr]), raw=True)
                    return
                elif new_value == "":
                    # Right hand side included but empty. Delete attribute.
                    script.db.database["areas"][areakey].pop(attr, None)
                    self.caller.msg("Attribute %s/%s was deleted." % (areakey, attr))
                    return
                else:
                    # Right hand side is set. Set attribute value.
                    
                    # TODO: Validation of specific attributes
                    
                    script.db.database["areas"][areakey][attr] = self.convert_from_string(new_value)
                    self.caller.msg("Attribute %s/%s was set." % (areakey, attr))
                    return
