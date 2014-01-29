"""
Example command set template module.

To create new commands to populate the cmdset, see
examples/command.py.

To extend the character command set:
  - copy this file up one level to gamesrc/commands and name it
    something fitting.
  - change settings.CMDSET_CHARACTER to point to the new module's
    CharacterCmdSet class
  - import/add commands at the end of CharacterCmdSet's add() method.

To extend Player cmdset:
  - like character set, but point settings.PLAYER on your new cmdset.

To extend Unloggedin cmdset:
  - like default set, but point settings.CMDSET_UNLOGGEDIN on your new cmdset.

To add a wholly new command set:
  - copy this file up one level to gamesrc/commands and name it
    something fitting.
  - add a new cmdset class
  - add it to objects e.g. with obj.cmdset.add(path.to.the.module.and.class)

"""

from ev import CmdSet, Command
from ev import default_cmds

#from contrib import menusystem, lineeditor
#from contrib import misc_commands
#from contrib import chargen


class MinimumCommands(CmdSet):
    """
    Implements an empty, example cmdset.
    """

    #key = "ExampleSet"

    def at_cmdset_creation(self):
        """
        This is the only method defined in a cmdset, called during
        its creation. It should populate the set with command instances.

        As and example we just add the empty base Command object.
        It prints some info.
        """
        self.add(default_cmds.CmdLook())
        self.add(default_cmds.CmdSay())
