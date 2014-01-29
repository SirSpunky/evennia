# -*- coding: utf-8 -*-
from django.conf import settings
from src.utils import utils, prettytable
from src.commands.default.muxcommand import MuxCommand
from src.commands.default.building import CmdTunnel as CmdTunnelDefault
from src.commands.default.building import ObjManipCommand
from src.utils import create, utils, search

try:
    # used by @set
    from ast import literal_eval as _LITERAL_EVAL
except ImportError:
    # literal_eval is not available before Python 2.6
    _LITERAL_EVAL = None

# used by @find
CHAR_TYPECLASS = settings.BASE_CHARACTER_TYPECLASS

class CmdAttr(ObjManipCommand):
    """
    @attr - set attributes

    Usage:
      @attr <obj>/<attr> = <value>
      @attr <obj>/<attr> =
      @attr <obj>/<attr>
      @attr *<player>/attr = <value>

    Sets attributes on objects. The second form clears
    a previously set attribute while the last form
    inspects the current value of the attribute
    (if any).

    The most common data to save with this command are strings and
    numbers. You can however also set Python primities such as lists,
    dictionaries and tuples on objects (this might be important for
    the functionality of certain custom objects).  This is indicated
    by you starting your value with one of {c'{n, {c"{n, {c({n, {c[{n
    or {c{ {n.
    Note that you should leave a space after starting a dictionary ('{ ')
    so as to not confuse the dictionary start with a colour code like \{g.
    Remember that if you use Python primitives like this, you must
    write proper Python syntax too - notably you must include quotes
    around your strings or you will get an error.

    """

    key = ".attr"
    aliases = [".a", ".set"]
    locks = "cmd:perm(set) or perm(Builders)"
    help_category = "Building"

    def convert_from_string(self, strobj):
        """
        Converts a single object in *string form* to its equivalent python
        type.

         Python earlier than 2.6:
        Handles floats, ints, and limited nested lists and dicts
        (can't handle lists in a dict, for example, this is mainly due to
        the complexity of parsing this rather than any technical difficulty -
        if there is a need for @set-ing such complex structures on the
        command line we might consider adding it).
         Python 2.6 and later:
        Supports all Python structures through literal_eval as long as they
        are valid Python syntax. If they are not (such as [test, test2], ie
        withtout the quotes around the strings), the entire structure will
        be converted to a string and a warning will be given.

        We need to convert like this since all data being sent over the
        telnet connection by the Player is text - but we will want to
        store it as the "real" python type so we can do convenient
        comparisons later (e.g.  obj.db.value = 2, if value is stored as a
        string this will always fail).
        """

        def rec_convert(obj):
            """
            Helper function of recursive conversion calls. This is only
            used for Python <=2.5. After that literal_eval is available.
            """
            # simple types
            try:
                return int(obj)
            except ValueError:
                pass
            try:
                return float(obj)
            except ValueError:
                pass
            # iterables
            if obj.startswith('[') and obj.endswith(']'):
                "A list. Traverse recursively."
                return [rec_convert(val) for val in obj[1:-1].split(',')]
            if obj.startswith('(') and obj.endswith(')'):
                "A tuple. Traverse recursively."
                return tuple([rec_convert(val) for val in obj[1:-1].split(',')])
            if obj.startswith('{') and obj.endswith('}') and ':' in obj:
                "A dict. Traverse recursively."
                return dict([(rec_convert(pair.split(":", 1)[0]),
                              rec_convert(pair.split(":", 1)[1]))
                             for pair in obj[1:-1].split(',') if ":" in pair])
            # if nothing matches, return as-is
            return obj

        if _LITERAL_EVAL:
            # Use literal_eval to parse python structure exactly.
            try:
                return _LITERAL_EVAL(strobj)
            except (SyntaxError, ValueError):
                # treat as string
                string = "{RNote: Value was converted to string. If you don't want this, "
                string += "use proper Python syntax, like enclosing strings in quotes.{n"
                self.caller.msg(string)
                return utils.to_str(strobj)
        else:
            # fall back to old recursive solution (does not support
            # nested lists/dicts)
            return rec_convert(strobj.strip())

    def func(self):
        "Implement the set attribute - a limited form of @py."

        caller = self.caller
        if not self.args:
            caller.msg("Usage: @set obj/attr = value. Use empty value to clear.")
            return

        # get values prepared by the parser
        value = self.rhs
        objname = self.lhs_objattr[0]['name']
        attrs = self.lhs_objattr[0]['attrs']

        if objname.startswith('*'):
            obj = caller.search_player(objname.lstrip('*'))
        else:
            obj = caller.search(objname)
        if not obj:
            return

        string = ""
        if not value:
            if self.rhs is None:
                # no = means we inspect the attribute(s)
                if not attrs:
                    attrs = [attr.key for attr in obj.attributes.all()]
                for attr in attrs:
                    if obj.attributes.has(attr):
                        value = obj.attributes.get(attr)
                        if isinstance(value, basestring):
                            value = '"%s"' % value
                        string += "\nAttribute %s/%s = %s" % (obj, attr, value)
                    else:
                        string += "\n%s has no attribute '%s'." % (obj, attr)
                    # we view it without parsing markup.
                self.caller.msg(string.strip(), raw=True)
                return
            else:
                # deleting the attribute(s)
                for attr in attrs:
                    if obj.attributes.has(attr):
                        val = obj.attributes.has(attr)
                        obj.attributes.remove(attr)
                        string += "\nDeleted attribute '%s' (= %s) from %s." % (attr, val, obj.name)
                    else:
                        string += "\n%s has no attribute '%s'." % (obj.name, attr)
                
                obj.start_scripts() # Restart all scripts on object
        else:
            # setting attribute(s). Make sure to convert to real Python type before saving.
            for attr in attrs:
                try:
                    if obj.attributes.has(attr):
                        action = "Modified"
                    else:
                        action = "Created"
                    obj.attributes.add(attr, self.convert_from_string(value))
                    string += "\n%s attribute %s/%s = %s" % (action, obj.name, attr, value)
                except SyntaxError:
                    # this means literal_eval tried to parse a faulty string
                    string = "{RCritical Python syntax error in your value. "
                    string += "Only primitive Python structures are allowed. "
                    string += "\nYou also need to use correct Python syntax. "
                    string += "Remember especially to put quotes around all "
                    string += "strings inside lists and dicts.{n"
                    
            obj.start_scripts() # Restart all scripts on object
        
        # send feedback
        caller.msg(string.strip('\n'))