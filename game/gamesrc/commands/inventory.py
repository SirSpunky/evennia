# -*- coding: utf-8 -*-
from django.conf import settings
from src.utils import utils, prettytable
from src.commands.default.muxcommand import MuxCommand


class CmdInventory(MuxCommand):
    """
    inventory

    Usage:
      inventory
      inv

    Shows your inventory.
    """
    key = "inventory"
    aliases = ["inv", "i"]
    locks = "cmd:all()"

    def func(self):
        "check inventory"
        items = self.caller.contents
        if not items:
            string = "You are not carrying anything."
        else:
            #table = prettytable.PrettyTable(["name", "desc", "weight"])
            #table.header = False
            #table.border = False
            #for item in items:
                #table.add_row(["{C%s{n" % item.name, item.db.desc, "Weight: " + str(item.total_weight) + " kg"])
            #    table.add_row(["{C%s{n" % item.name, item.db.desc, "{w" + str(item.total_weight) + " kg{n"])
                #table.add_row(["{C%s{n" % item.name, item.db.desc and item.db.desc or ""])
            #string = "{wYou are carrying:\n\n%s" % (table)
            string = "You are carrying {w%g{n of {w%g kg:{n\n\n%s" % (self.caller.contents_weight, self.caller.max_contents_weight, self.caller.return_contents())
            #string = "You are carrying:\n"
            #string += "\n\nWeight: {w%s/%s kg{n\n" % (self.caller.contents_weight, self.caller.max_inventory_weight)
            #string += str(table)
            #(%s/%s kg):\n%s" % (self.caller.contents_weight, self.caller.max_inventory_weight, table)
        self.caller.msg(string)