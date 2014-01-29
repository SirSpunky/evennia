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


class CmdCreate(MuxCommand):
    """
    Creates a new object or character.

    Usage:
        .create <template_name>|object|character

    Details:
        .create <template_name> : Creates a new object or character from template <template_name>. Use ".db list" for a list of all available object and character templates.
        .create object <name> : Creates a blank new object called <name>.
        .create character <name> : Creates a blank new character called <name>.

    See also: .db
    """

    key = ".create"
    aliases = [".c"]
    locks = "cmd:perm(create) or perm(Builders)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        location = caller.location
        
        if not location:
            location = caller
            
        # Parse input
        target = None
        name = None
        if self.lhs:
            target = self.lhs.split(' ', 1)[0]
            if len(self.lhs.split(' ', 1)) > 1:
                name = self.lhs.split(' ', 1)[1]
        
        if not target:
            caller.msg("Which object do you wish create?")
            return
        
        # Find global script
        script_key = "GlobalDatabase"
        script = ev.search_script(script_key)
        if not script:
            caller.msg("Global script by name '%s' could not be found." % script_key)
            return
        script = script[0] # all ev.search_* methods always return lists
        
        # Make sure the "template_objects" dictionary already exists in the global database script.
        if "template_objects" not in script.db.database:
            script.db.database["template_objects"] = {}

        lockstring = "control:id(%s);examine:perm(Builders);delete:id(%s) or perm(Wizards)" % (caller.id, caller.id)



        # Create blank object
        if target == "object" or target == "obj":
            typeclass = settings.BASE_OBJECT_TYPECLASS
        
            new_obj = create.create_object(typeclass, "untitled object", location, home=location, locks=lockstring, report_to=caller)
            new_obj.db.desc = ''
        
        # Create blank character
        elif target == "character" or target == "char":
            typeclass = settings.BASE_CHARACTER_TYPECLASS

            new_obj = create.create_object(typeclass, "untitled character", location, home=location, locks=lockstring, report_to=caller)
            new_obj.db.desc = ''
        
        # Create object/character from template
        else:
            target = self.lhs
            name = self.rhs
            
            # Search for target in template database
            if not target in script.db.database["template_objects"]:
                caller.msg("Cannot find template '%s'." % target)
                return
            
            old_obj = script.db.database["template_objects"][target]["object"]
            
            from game.gamesrc.utils.copy_object_recursive import copy_object_recursive
            new_obj = copy_object_recursive(old_obj)
            
            # Set object location
            new_obj.home = location
            new_obj.move_to(location, quiet=True)
            
            new_obj.start_scripts()
            if new_obj.db.is_template:
                del new_obj.db.is_template
        
        
        # Set object name if supplied
        if name:
            new_obj.key = name
            
        caller.msg("Created %s." % new_obj.name)
        location.msg_contents("%s creates %s." % (caller.name, new_obj.name), exclude=caller)




        #if not self.args:
        #    string = "Usage: @create[/drop] <newname>[;alias;alias...] [:typeclass_path]"
        #    caller.msg(string)
        #    return
        #
        ## create the objects
        #for objdef in self.lhs_objs:
        #    string = ""
        #    name = objdef['name']
        #    aliases = objdef['aliases']
        #    typeclass = objdef['option']
        #
        #    # create object (if not a valid typeclass, the default
        #    # object typeclass will automatically be used)
        #    lockstring = "control:id(%s);examine:perm(Builders);delete:id(%s) or perm(Wizards)" % (caller.id, caller.id)
        #    obj = create.create_object(typeclass, name, caller,
        #                               home=caller, aliases=aliases,
        #                               locks=lockstring, report_to=caller)
        #    if not obj:
        #        continue
        #    if aliases:
        #        string = "You create a new %s: %s (aliases: %s)."
        #        string = string % (obj.typeclass.typename, obj.name, ", ".join(aliases))
        #    else:
        #        string = "You create a new %s: %s."
        #        string = string % (obj.typeclass.typename, obj.name)
        #    
        #    # set a default desc
        #    if not obj.db.desc:
        #        obj.db.desc = "You see nothing special."
        #
        #    # Set object location
        #    if caller.location:
        #        obj.home = caller.location
        #        obj.move_to(caller.location, quiet=True)
        #    
        #if string:
        #    self.caller.msg(string)