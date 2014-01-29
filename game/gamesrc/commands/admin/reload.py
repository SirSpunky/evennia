# -*- coding: utf-8 -*-
from django.conf import settings
from src.utils import utils, prettytable
from src.commands.default.muxcommand import MuxCommand
from src.commands.default.system import CmdReload as CmdReloadDefault


class CmdReload(CmdReloadDefault):
    """
    Reload the system

    Usage:
      .reload [reason]

    This restarts the server. The Portal is not
    affected. Non-persistent scripts will survive a .reload (use
    .reset to purge) and at_reload() hooks will be called.
    """
    key = ".reload"
    aliases = [".rel",".restart",".res",".r"]
    locks = "cmd:perm(reload) or perm(Immortals)"
    help_category = "System"
