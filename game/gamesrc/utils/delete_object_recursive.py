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


def delete_object_recursive(obj):
    for content in obj.contents:
        delete_object_recursive(content)
    success = obj.delete()
    return success
#
#def delete_object(obj):
#    # helper function for deleting a single object
#    string = ""
#    obj = caller.search(objname)
#    if not obj:
#        self.caller.msg(" (Objects to destroy must either be local or specified with a unique #dbref.)")
#        return ""
#    if (not "override" in self.switches and
#        obj.dbid == int(settings.CHARACTER_DEFAULT_HOME.lstrip("#"))):
#        return "\nYou are trying to delete CHARACTER_DEFAULT_HOME. If you want to do this, use the /override switch."
#    objname = obj.name
#    if not obj.access(caller, 'delete'):
#        return "\nYou don't have permission to delete %s." % objname
#    if obj.player and not 'override' in self.switches:
#        return "\nObject %s is controlled by an active player. Use /override to delete anyway." % objname
#
#    had_exits = hasattr(obj, "exits") and obj.exits
#    had_objs = hasattr(obj, "contents") and any(obj for obj in obj.contents
#                                                if not (hasattr(obj, "exits") and obj not in obj.exits))
#    # do the deletion
#    okay = obj.delete()
#    if not okay:
#        string += "\nERROR: %s not deleted, probably because at_obj_delete() returned False." % objname
#    else:
#        string += "\n%s was destroyed." % objname
#        if had_exits:
#            string += " Exits to and from %s were destroyed as well." % objname
#        if had_objs:
#            string += " Objects inside %s were moved to their homes." % objname
#    return string