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


def copy_object_recursive(old_obj):
    new_obj = ObjectDB.objects.copy_object(old_obj)
    for old_content in old_obj.contents:
        new_content = copy_object_recursive(old_content)
        new_content.location = new_obj
    return new_obj
