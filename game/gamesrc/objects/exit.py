"""

Template module for Exits

Copy this module up one level and name it as you like, then
use it as a template to create your own Exits.

To make the default commands (such as @dig/@open) default to creating exits
of your new type, change settings.BASE_EXIT_TYPECLASS to point to
your new class, e.g.

settings.BASE_EXIT_TYPECLASS = "game.gamesrc.objects.myexit.MyExit"

Note that objects already created in the database will not notice
this change, you have to convert them manually e.g. with the
@typeclass command.

"""
#from ev import Exit as DefaultExit
from game.gamesrc.objects.object import Object
from src.commands import cmdset, command


class Exit(Object):
    """
    This is the base exit object - it connects a location to another.
    This is done by the exit assigning a "command" on itself with the
    same name as the exit object (to do this we need to remember to
    re-create the command when the object is cached since it must be
    created dynamically depending on what the exit is called). This
    command (which has a high priority) will thus allow us to traverse
    exits simply by giving the exit-object's name on its own.
    """

    # Helper classes and methods to implement the Exit. These need not
    # be overloaded unless one want to change the foundation for how
    # Exits work. See the end of the class for hook methods to overload.

    def create_exit_cmdset(self, exidbobj):
        """
        Helper function for creating an exit command set + command.

        The command of this cmdset has the same name as the Exit object
        and allows the exit to react when the player enter the exit's name,
        triggering the movement between rooms.

        Note that exitdbobj is an ObjectDB instance. This is necessary
        for handling reloads and avoid tracebacks if this is called while
        the typeclass system is rebooting.
        """
        class ExitCommand(command.Command):
            """
            This is a command that simply cause the caller
            to traverse the object it is attached to.
            """
            obj = None

            def func(self):
                "Default exit traverse if no syscommand is defined."

                if self.obj.access(self.caller, 'traverse'):
                    # we may traverse the exit.
                    self.obj.at_traverse(self.caller, self.obj.destination)
                else:
                    # exit is locked
                    if self.obj.db.err_traverse:
                        # if exit has a better error message, let's use it.
                        self.caller.msg(self.obj.db.err_traverse)
                    else:
                        # No shorthand error message. Call hook.
                        self.obj.at_failed_traverse(self.caller)

        # create an exit command. We give the properties here,
        # to always trigger metaclass preparations
        cmd = ExitCommand(key=exidbobj.db_key.strip().lower(),
                          aliases=exidbobj.aliases.all(),
                          locks=str(exidbobj.locks),
                          auto_help=False,
                          destination=exidbobj.db_destination,
                          arg_regex=r"$",
                          is_exit=True,
                          obj=exidbobj)
        # create a cmdset
        exit_cmdset = cmdset.CmdSet(None)
        exit_cmdset.key = '_exitset'
        exit_cmdset.priority = 9
        exit_cmdset.duplicates = True
        # add command to cmdset
        exit_cmdset.add(cmd)
        return exit_cmdset

    # Command hooks
    def basetype_setup(self):
        """
        Setup exit-security

        You should normally not need to overload this - if you do make sure you
        include all the functionality in this method.
        """
        super(Exit, self).basetype_setup()

        # setting default locks (overload these in at_object_creation()
        self.locks.add(";".join(["puppet:false()", # would be weird to puppet an exit ...
                                 "traverse:all()", # who can pass through exit by default
                                 "get:false()"]))   # noone can pick up the exit

        # an exit should have a destination (this is replaced at creation time)
        if self.dbobj.location:
            self.destination = self.dbobj.location

    @property
    def name(self):
        return "%cc" + self.key + "{n"
    
    @property
    def name_upper(self):
        return "%cc" + self.key[0].upper() + self.key[1:] + "{n"
    
    def at_cmdset_get(self):
        """
        Called when the cmdset is requested from this object, just before the
        cmdset is actually extracted. If no Exit-cmdset is cached, create
        it now.
        """
        
        if self.ndb.exit_reset or not self.cmdset.has_cmdset("_exitset", must_be_default=True):
            # we are resetting, or no exit-cmdset was set. Create one dynamically.
            self.cmdset.add_default(self.create_exit_cmdset(self.dbobj), permanent=False)
            self.ndb.exit_reset = False

    # this and other hooks are what usually can be modified safely.

    def at_object_creation(self):
        "Called once, when object is first created (after basetype_setup)."
        pass

    def at_traverse(self, traversing_object, target_location):
        """
        This implements the actual traversal. The traverse lock has already been
        checked (in the Exit command) at this point.
        """
        source_location = traversing_object.location
        if traversing_object.move_to(target_location):
            self.at_after_traverse(traversing_object, source_location)
        else:
            if self.db.err_traverse:
                # if exit has a better error message, let's use it.
                self.caller.msg(self.db.err_traverse)
            else:
                # No shorthand error message. Call hook.
                self.at_failed_traverse(traversing_object)

    def at_after_traverse(self, traversing_object, source_location):
        """
        Called after a successful traverse.
        """
        pass

    def at_failed_traverse(self, traversing_object):
        """
        This is called if an object fails to traverse this object for some
        reason. It will not be called if the attribute "err_traverse" is
        defined, that attribute will then be echoed back instead as a
        convenient shortcut.

        (See also hooks at_before_traverse and at_after_traverse).
        """
        traversing_object.msg("You cannot go there.")
    
    def get_opposite_exit(self):
        for obj in self.destination.contents:
            if isinstance(obj, Exit) and obj.destination == self.location:
                return obj
                #if self.key == "east" and obj.key == "west":
                #    return obj
                #elif self.key == "north" and obj.key == "south":
                #    return obj
                #elif self.key == "west" and obj.key == "east":
                #    return obj
                #elif self.key == "south" and obj.key == "north":
                #    return obj
                #elif self.key == "up" and obj.key == "down":
                #    return obj
                #elif self.key == "down" and obj.key == "up":
                #    return obj