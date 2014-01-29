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


class CmdObjects(MuxCommand):
    """
    .objects - Give a summary of object types in database

    Usage:
      .objects [<nr>]

    Gives statictics on objects in database as well as
    a list of <nr> latest objects in database. If not
    given, <nr> defaults to 100.
    """
    key = ".objects"
    aliases = [".obj"]
    locks = "cmd:perm(listobjects) or perm(Builders)"
    help_category = "System"

    def func(self):
        "Implement the command"

        caller = self.caller

        if self.args and self.args.isdigit():
            nlim = int(self.args)
        else:
            nlim = 100

        nobjs = ObjectDB.objects.count()
        base_char_typeclass = settings.BASE_CHARACTER_TYPECLASS
        nchars = ObjectDB.objects.filter(db_typeclass_path=base_char_typeclass).count()
        nrooms = ObjectDB.objects.filter(db_location__isnull=True).exclude(db_typeclass_path=base_char_typeclass).count()
        nexits = ObjectDB.objects.filter(db_location__isnull=False, db_destination__isnull=False).count()
        nother = nobjs - nchars - nrooms - nexits

        # total object sum table
        totaltable = prettytable.PrettyTable(["{wtype", "{wcomment", "{wcount", "{w%%"])
        totaltable.align = 'l'
        totaltable.add_row(["Characters", "(BASE_CHARACTER_TYPECLASS)", nchars, "%.2f" % ((float(nchars) / nobjs) * 100)])
        totaltable.add_row(["Rooms", "(location=None)", nrooms, "%.2f" % ((float(nrooms) / nobjs) * 100)])
        totaltable.add_row(["Exits", "(destination!=None)", nexits, "%.2f" % ((float(nexits) / nobjs) * 100)])
        totaltable.add_row(["Other", "", nother, "%.2f" % ((float(nother) / nobjs) * 100)])

        # typeclass table
        typetable = prettytable.PrettyTable(["{wtypeclass", "{wcount", "{w%%"])
        typetable.align = 'l'
        dbtotals = ObjectDB.objects.object_totals()
        for path, count in dbtotals.items():
            typetable.add_row([path, count, "%.2f" % ((float(count) / nobjs) * 100)])

        # last N table
        objs = ObjectDB.objects.all().order_by("db_date_created")[max(0, nobjs - nlim):]
        latesttable = prettytable.PrettyTable(["{wcreated",
                                               "{wdbref",
                                               "{wname",
                                               "{wlocation",
                                               "{wtypeclass"])
        latesttable.align = 'l'
        for obj in objs:
            latesttable.add_row([utils.datetime_format(obj.date_created),
                                 obj.dbref, obj.key, obj.location.dbref if obj.location else "", obj.typeclass.path])

        string = "\n{wObject subtype totals (out of %i Objects):{n\n%s" % (nobjs, totaltable)
        string += "\n{wObject typeclass distribution:{n\n%s" % typetable
        string += "\n{wLast %s Objects created:{n\n%s" % (min(nobjs, nlim), latesttable)
        caller.msg(string)