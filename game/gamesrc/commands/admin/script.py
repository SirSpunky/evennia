# -*- coding: utf-8 -*-

import traceback
import os
import datetime
import time
import sys
import django
import twisted
from time import time as timemeasure

from django.conf import settings
from src.server.caches import get_cache_sizes
from src.server.sessionhandler import SESSIONS
from src.scripts.models import ScriptDB
from src.objects.models import ObjectDB
from src.players.models import PlayerDB
from src.utils import logger, utils, gametime, create, is_pypy, prettytable
from src.utils.utils import crop
from src.commands.default.muxcommand import MuxCommand

from game.gamesrc.scripts import *


class CmdScript(MuxCommand):
    """
    attach scripts

    Usage:
      @script[/switch] <obj> [= <script.path or scriptkey>]

    Switches:
      start - start all non-running scripts on object, or a given script only
      stop - stop all scripts on objects, or a given script only

    If no script path/key is given, lists all scripts active on the given
    object.
    Script path can be given from the base location for scripts as given in
    settings. If adding a new script, it will be started automatically
    (no /start switch is needed). Using the /start or /stop switches on an
    object without specifying a script key/path will start/stop ALL scripts on
    the object.
    """

    key = ".script"
    aliases = ["@script","@addscript"]
    locks = "cmd:perm(script) or perm(Builders)"
    help_category = "Building"

    def func(self):
        "Do stuff"

        caller = self.caller

        if not self.args:
            string = "Usage: @script[/switch] <obj> [= <script.path or script key>]"
            caller.msg(string)
            return

        obj = caller.search(self.lhs)
        if not obj:
            return

        string = ""
        if not self.rhs:
            # no rhs means we want to operate on all scripts
            scripts = obj.scripts.all()
            if not scripts:
                string += "No scripts defined on %s." % obj.key
            elif not self.switches:
                # view all scripts
                from src.commands.default.system import format_script_list
                string += format_script_list(scripts)
            elif "start" in self.switches:
                num = sum([obj.scripts.start(script.key) for script in scripts])
                string += "%s scripts started on %s." % (num, obj.key)
            elif "stop" in self.switches:
                for script in scripts:
                    string += "Stopping script %s on %s." % (script.key,
                                                             obj.key)
                    script.stop()
                string = string.strip()
            obj.scripts.validate()
        else: # rhs exists
            if not self.switches:
                # adding a new script, and starting it
                #ok = obj.scripts.add(self.rhs, autostart=True)
                ok = obj.scripts.add(globals()[self.rhs], autostart=True)
                if not ok:
                    string += "\nScript %s could not be added and/or started on %s." % (self.rhs, obj.key)
                else:
                    string = "Script {w%s{n successfully added and started on %s." % (self.rhs, obj.key)

            else:
                paths = [self.rhs] + ["%s.%s" % (prefix, self.rhs)
                                      for prefix in settings.SCRIPT_TYPECLASS_PATHS]
                if "stop" in self.switches:
                    # we are stopping an already existing script
                    for path in paths:
                        ok = obj.scripts.stop(path)
                        if not ok:
                            string += "\nScript %s could not be stopped. Does it exist?" % path
                        else:
                            string = "Script stopped and removed from object."
                            break
                if "start" in self.switches:
                    # we are starting an already existing script
                    for path in paths:
                        ok = obj.scripts.start(path)
                        if not ok:
                            string += "\nScript %s could not be (re)started." % path
                        else:
                            string = "Script started successfully."
                            break
        caller.msg(string.strip())
