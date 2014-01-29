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


class CmdDb(MuxCommand):
    """
    View or modify object and character templates from the in-game database.

    Usage:
        .db list|list objects|list characters|list <keyword>|add <name>|delete <name>

    Details:
        .db list : Lists all object and character templates.
        .db list objects : Lists all object templates.
        .db list characters : Lists all character templates.
        .db list <keyword> : Lists all templates matching <keyword>.
        .db add <name> : Add object or character <name> from room to database as template.
        .db delete <name> : Delete object or character template <name> from the database. Does not delete any objects already placed.

    See also: .create
    """

    key = ".db"
    aliases = [".templates"]
    locks = "cmd:perm(create) or perm(Builders)"
    help_category = "Building"

    def func(self):
        
        # Find global script
        script_key = "GlobalDatabase"
        script = ev.search_script(script_key)
        if not script:
            self.caller.msg("Global script by name '%s' could not be found." % script_key)
            return
        script = script[0] # all ev.search_* methods always return lists
        
        # Make sure the "template_objects" dictionary already exists in the global database script.
        if "template_objects" not in script.db.database:
            script.db.database["template_objects"] = {}
        
        # Parse input
        command = None
        target = None
        if self.lhs:
            command = self.lhs.split(' ', 1)[0]
            if len(self.lhs.split(' ', 1)) > 1:
                target = self.lhs.split(' ', 1)[1]
        
        

        
        if command == "delete":
            if not target:
                self.caller.msg("Which template do you wish to delete?")
                return
            
            if not target in script.db.database["template_objects"]:
                self.caller.msg("Cannot find template '%s'." % target)
                return
            
            obj = script.db.database["template_objects"][target]["object"]
            
            from game.gamesrc.utils.delete_object_recursive import delete_object_recursive
            okay = delete_object_recursive(obj)
            if not okay:
                string += "\nERROR: Object %s could not be deleted, probably because at_obj_delete() returned False." % obj.name
                return
            
            script.db.database["template_objects"].pop(target, None)
            
            self.caller.msg("Template '%s' was deleted." % target)
        
        elif command == "add":
            if not target:
                self.caller.msg("Which object do you wish to add?")
                return
            
            old_obj = self.caller.search(target, location=[self.caller, self.caller.location])
            
            if not old_obj:
                self.caller.msg("Cannot find %s in this room or your inventory." % target)
                return
            
            if self.rhs:
                key = self.rhs.lower()
            else:
                key = old_obj.key.lower()
            
            if key in script.db.database["template_objects"]:
                self.caller.msg("There's already a template with that name. Use '.db add <target> = <name>' to add it under a different name.")
                return
            
            obj_type = old_obj.__class__.__name__.lower()
            if obj_type != "object" and obj_type != "character":
                self.caller.msg("Object type '%s' not supported." % obj_type)
                return
            
            from game.gamesrc.utils.copy_object_recursive import copy_object_recursive
            obj = copy_object_recursive(old_obj)
            obj.location = None
            obj.stop_scripts()
            obj.db.is_template = True

            template = {}
            template["name"] = obj.key
            template["desc"] = obj.db.desc
            template["type"] = obj_type
            template["object"] = obj
            
            script.db.database["template_objects"][key] = template
            
            self.caller.msg("Template '%s' was added." % key)
        
        else:
            filter = ''
            
            if command != "list" and not target:
                target = command
            
            if target == "objects":
                # List objects
                filter = 'objects'
            elif target == "characters" or target == "chars":
                # List characters
                filter = 'characters'
            elif target:
                # List search
                filter = 'search'

            # Draw table
            from src.utils import utils, prettytable
        
            table = prettytable.PrettyTable(["Name", "Type", "Desc"])
            table.header = True
            table.border = False
            for key, item in script.db.database["template_objects"].iteritems():
                if filter == "objects" and item["type"] != "object":
                    continue
                if filter == "characters" and item["type"] != "character":
                    continue
                if filter == "search" and target not in key:
                    continue
                
                if item["type"] == "character":
                    color = "{Y"
                else:
                    color = "{x"
                
                table.add_row([color + key + "{n", color + item["type"] + "{n", "{W" + item["desc"] + "{n"])
            
            self.caller.msg("Templates:\n\n%s" % unicode(table))