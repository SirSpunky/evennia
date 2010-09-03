"""
The base Command class.

All commands in Evennia inherit from the 'Command' class in this module. 

"""

from src.permissions import permissions
from src.utils.utils import is_iter

class CommandMeta(type):
    """
    This metaclass makes some minor on-the-fly convenience fixes to the command
    class in case the admin forgets to put things in lowercase etc. 
    """    
    def __init__(mcs, *args, **kwargs):
        """
        Simply make sure all data are stored as lowercase and
        do checking on all properties that should be in list form.
        """
        mcs.key = mcs.key.lower()
        if mcs.aliases and not is_iter(mcs.aliases):
            mcs.aliases = mcs.aliases.split(',')
        mcs.aliases = [str(alias).strip().lower() for alias in mcs.aliases]
        if mcs.permissions and not is_iter(mcs.permissions) :
            mcs.permissions = mcs.permissions.split(',')    
        mcs.permissions = [str(perm).strip().lower() for perm in mcs.permissions]
        mcs.help_category = mcs.help_category.lower()
        super(CommandMeta, mcs).__init__(*args, **kwargs)


#    The Command class is the basic unit of an Evennia command; when
#    defining new commands, the admin subclass this class and
#    define their own parser method to handle the input. The
#    advantage of this is inheritage; commands that have similar
#    structure can parse the input string the same way, minimizing
#    parsing errors. 
 
class Command(object):
    """
    Base command

    Usage:
      command [args]
    
    This is the base command class. Inherit from this
    to create new commands.         
    
    The cmdhandler makes the following variables available to the 
    command methods (so you can always assume them to be there):
    self.caller - the game object calling the command
    self.cmdstring - the command name used to trigger this command (allows
                     you to know which alias was used, for example)
    cmd.args - everything supplied to the command following the cmdstring
               (this is usually what is parsed in self.parse())
    cmd.cmdset - the cmdset from which this command was matched (useful only
                seldomly, notably for help-type commands, to create dynamic
                help entries and lists)
    cmd.obj - the object on which this command is defined. If a default command,
                 this is usually the same as caller. 

    (Note that this initial string is also used by the system to create the help
    entry for the command, so it's a good idea to format it similar to this one)
    """
    # Tie our metaclass, for some convenience cleanup
    __metaclass__ = CommandMeta

    # the main way to call this command (e.g. 'look')
    key = "command"
    # alternative ways to call the command (e.g. 'l', 'glance', 'examine')
    aliases = []
    # a list of permission strings or comma-separated string limiting 
    # access to this command.
    permissions = []
    # used by the help system to group commands in lists.
    help_category = "default"
    # There is also the property 'obj'. This gets set by the system 
    # on the fly to tie this particular command to a certain in-game entity.
    # self.obj should NOT be defined here since it will not be overwritten 
    # if it already exists. 
    
    def __str__(self):
        "Print the command"
        return self.key
    
    def __eq__(self, cmd):
        """
        Compare two command instances to each other by matching their
        key and aliases.
        input can be either a cmd object or the name of a command.
        """
        if type(cmd) != self:
            return self.match(cmd)
        return self.match(cmd.key)

    def __contains__(self, query):
        """
        This implements searches like 'if query in cmd'. It's a fuzzy matching
        used by the help system, returning True if query can be found
        as a substring of the commands key or its aliases. 

        input can be either a command object or a command name.
        """
        if type(query) == type(Command()):
            query = query.key
        return (query in self.key) or \
               (sum([query in alias for alias in self.aliases]) > 0)

    def match(self, cmdname):
        """
        This is called by the system when searching the available commands,
        in order to determine if this is the one we wanted. cmdname was
        previously extracted from the raw string by the system.
        cmdname is always lowercase when reaching this point.
        """
        return (cmdname == self.key) or (cmdname in self.aliases)

    def has_perm(self, srcobj):
        """
        This hook is called by the cmdhandler to determine if srcobj
        is allowed to execute this command. It should return a boolean
        value and is not normally something that need to be changed since
        it's using the Evennia permission system directly. 
        """
        return permissions.has_perm(srcobj, self, 'cmd')
    
    # Common Command hooks         

    def parse(self):
        """
        Once the cmdhandler has identified this as the command we
        want, this function is run. If many of your commands have
        a similar syntax (for example 'cmd arg1 = arg2') you should simply
        define this once and just let other commands of the same form
        inherit from this. See the docstring of this module for 
        which object properties are available to use 
        (notably self.args).
        """        
        pass
        
    def func(self):
        """
        This is the actual executing part of the command. 
        It is called directly after self.parse(). See the docstring
        of this module for which object properties are available
        (beyond those set in self.parse()) 
        """        
        string = "Command '%s' was executed with arg string '%s'." 
        self.caller.msg(string % (self.key, self.args))