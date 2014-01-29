# -*- coding: utf-8 -*-
from django.conf import settings
from src.utils import utils, prettytable
from src.commands.default.muxcommand import MuxCommand
from src.commands.default.building import CmdTunnel as CmdTunnelDefault
from src.utils import create, utils, search



class CmdTag(MuxCommand):
    """
    handles tagging

    Usage:
      .tag <obj> [= <tag>[:<category>]]
      .tag search <tag>

      @tag[/del] <obj> [= <tag>[:<category>]]
      @tag/search <tag>

    Manipulates and lists tags on objects. Tags allow for quick
    grouping of and searching for objects.  If only <obj> is given,
    list all tags on the object.  If search is used, list objects
    with the given tag.
    The category can be used for grouping tags themselves.
    """

    key = ".tag"
    aliases = [".t"]
    locks = "cmd:perm(tag) or perm(Builders)"
    help_category = "Building"

    def func(self):
        "Implement the @tag functionality"

        # Parse input
        target = None
        remaining = None
        if self.lhs:
            target = self.lhs.split(' ', 1)[0]
            if len(self.lhs.split(' ', 1)) > 1:
                remaining = self.lhs.split(' ', 1)[1]

        if target == "search":
            # Search by tag
            tag = remaining
            category = None
            search_category = None
            if ":" in tag:
                tag, category = [part.strip() for part in tag.split(":", 1)]
                search_category = "object%s" % category
            #print "tag search:", tag, search_category
            objs = search.search_tag(tag, category=search_category)
            nobjs = len(objs)
            if nobjs > 0:
                string = "Found %i object%s with tag '%s'%s:\n %s" % (nobjs,
                                                       "s" if nobjs > 1 else "",
                                                       tag,
                                                       " (category: %s)" % category if category else "",
                                                       ", ".join("%s(#%i)" % (o.key, o.dbid) for o in objs))
            else:
                string = "No objects found with tag '%s%s'." % (tag,
                                                        " (category: %s)" % category if category else "")
            self.caller.msg(string)
            return

        obj = None
        if not self.lhs:
            obj = self.caller.location

        if self.rhs:            
            # Add/remove tag on object ("=" was found)
            if not obj:
                obj = self.caller.search(self.lhs)
            if not obj:
                return
            tag = self.rhs
            category = None
            
            if ":" in tag:
                tag, category = [part.strip() for part in tag.split(":", 1)]
                
            if obj.tags.get(tag):
                # Tag exists, remove the tag
                obj.tags.remove(tag, category=category)
                string = "Removed tag '%s'%s from %s." % (tag,
                                                    " (category: %s)" % category if category else "",
                                                    obj)
                obj.on_remove_tag(tag) # Call hook function
            else:    
                # Tag doesn't exist, add the tag
                obj.tags.add(tag, category=category)
                string = "Added tag '%s'%s to %s." % (tag,
                                                      " (category: %s)" % category if category else "",
                                                      obj)
                obj.on_add_tag(tag) # Call hook function
            self.caller.msg(string)

        else:
            # List tags on object (no "=" found)
            if not obj:
                obj = self.caller.search(self.args)
            if not obj:
                return
            tagtuples = obj.tags.all(return_key_and_category=True)
            ntags = len(tagtuples)
            tags = [tup[0] for tup in tagtuples]
            categories = [" (category: %s)" % tup[1] if tup[1] else "" for tup in tagtuples]
            if ntags:
                string = "Tag%s on %s: %s" % ("s" if ntags > 1 else "", obj,
                                        ", ".join("'%s'%s" % (tags[i], categories[i]) for i in range(ntags)))
            else:
                string = "No tags attached to %s." % obj
            self.caller.msg(string)
            
