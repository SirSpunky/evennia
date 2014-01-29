# -*- coding: utf-8 -*-
from django.conf import settings
from src.utils import utils, prettytable
from src.commands.default.muxcommand import MuxCommand


class CmdDrop(MuxCommand):
    """
    drop

    Usage:
      drop <obj>

    Lets you drop an object from your inventory into the
    location you are currently in.
    """

    key = "drop"
    locks = "cmd:all()"

    def func(self):
        "Implement command"

        caller = self.caller
        if not self.args:
            caller.msg("Drop what?")
            return

        # Because the DROP command by definition looks for items
        # in inventory, call the search function using location = caller
        obj = caller.search(self.args, location=caller)

        # now we send it into the error handler (this will output consistent
        # error messages if there are problems).
        #obj = AT_SEARCH_RESULT(caller, self.args, results, False,
        #                      nofound_string="You don't carry %s." % self.args,
        #                      multimatch_string="You carry more than one %s:" % self.args)
        if not obj:
            return

        obj.move_to(caller.location, quiet=True)
        caller.msg("You drop %s." % (obj.name,))
        caller.location.msg_contents("%s drops %s." %
                                         (caller.name, obj.name),
                                         exclude=caller)
        # Call the object script's at_drop() method.
        obj.at_drop(caller)