# -*- coding: utf-8 -*-
from django.conf import settings
from src.utils import utils, prettytable
from src.commands.default.muxcommand import MuxCommand
from src.commands.default.building import CmdTunnel as CmdTunnelDefault
from src.utils import create, utils, search


class CmdDig(MuxCommand):
    """
    Build a new room, connected to your current room.

    Usage:
      .dig <direction> [roomname] [= from_room]

    Example:
      .dig n
      .dig n old house
    
    Build a new room, connected to your current room. If coordinates are available and a room already occupies the new position, no new room will be created, but your current room will be connected to that room instead.
    
    If from_room is specified (either dbref or name), will use that room as current location to dig from.
    """

    key = ".dig"
    locks = "cmd: perm(dig) or perm(tunnel) or perm(Builders)"
    help_category = "Building"

    # store the direction, full name and its opposite
    directions = {"n": ("north", "s"),
                  #"ne": ("northeast", "sw"),
                  "e": ("east", "w"),
                  #"se": ("southeast", "nw"),
                  "s": ("south", "n"),
                  #"sw": ("southwest", "ne"),
                  "w": ("west", "e"),
                  #"nw": ("northwest", "se"),
                  #"i": ("in", "o"),
                  #"o": ("out", "i"),
                  "u": ("up", "d"),
                  "d": ("down", "u")}
    
    def func(self):
        caller = self.caller
        
        # Get current location to dig from
        location = None
        if self.rhs:
            location = caller.search(self.rhs, global_search=True)
            if not location:
                caller.msg("Cannot find location '%s'." % self.rhs)
                return
        
        if not location:
            location = caller.location
        
        if not location:
            caller.msg("You must be standing in a room in order to dig from it.")
            return
        
        # Parse input
        direction = None
        roomname = None
        if self.lhs:
            direction = self.lhs.split(' ', 1)[0]
            if len(self.lhs.split(' ', 1)) > 1:
                roomname = self.lhs.split(' ', 1)[1]

        if not direction or direction not in self.directions:
            caller.msg("You can only dig in the following directions: %s." % ",".join(sorted(self.directions.keys())))
            return

        # Retrieve all input and parse it
        exitshort = direction
        exitname, backexitshort = self.directions[exitshort]
        backexitname = self.directions[backexitshort][0]
        new_room = None
        lockstring = "control:id(%s) or perm(Immortals); delete:id(%s) or perm(Wizards); edit:id(%s) or perm(Wizards)"
        lockstring = lockstring % (caller.dbref, caller.dbref, caller.dbref)

        # Check if exit already exists in that direction.
        from game.gamesrc.objects.exit import Exit
        for obj in location.contents:
            if isinstance(obj, Exit) and obj.key == exitname:
                caller.msg("There's already an exit %s." % exitname)
                
                # Fix: Updates coordinates on nearby room
                #if location.db.x != None and location.db.y != None and location.db.z != None:
                #    new_x, new_y, new_z = location.get_nearby_coordinates(direction)
                #    obj.destination.db.x = new_x
                #    obj.destination.db.y = new_y
                #    obj.destination.db.z = new_z
                return

        # Check for nearby room in the direction we're digging.
        if location.db.x != None and location.db.y != None and location.db.z != None:
            new_room = location.get_nearby_room(direction)
        
        if new_room:
            # Digging into existing room
            
            if roomname:
                caller.msg("There's already a room in that direction: %s (%s). Type '.dig %s' to create an exit to it." % (new_room.name, new_room.dbref, exitshort))
                return

            
            if caller.location == location:
                caller.msg("You open up a new way {C%s{n into %s." % (exitname, new_room.name))
                location.msg_contents("%s opens up a new way {C%s{n." % (caller.name, exitname), exclude=caller)
            else:
                caller.msg("You open up a new way {C%s{n from %s into %s." % (exitname, location.name, new_room.name))
                location.msg_contents("A new way appears {C%s{n." % (exitname), exclude=caller)
                new_room.location.msg_contents("A new way appears {C%s{n." % (backexitname), exclude=caller)

        else:
            # Create new room
            
            if not roomname:
                roomname = "untitled room"
            
            typeclass = settings.BASE_ROOM_TYPECLASS
    
            new_room = create.create_object(typeclass, roomname, report_to=caller)
            new_room.locks.add(lockstring)
            
            if caller.location == location:
                caller.msg("You create a new room {C%s{n called '%s'." % (exitname, new_room.name))
                location.msg_contents("%s creates a new room {C%s{n." % (caller.name, exitname), exclude=caller)
            else:
                caller.msg("You create a new room {C%s{n from %s called '%s'." % (exitname, location.name, new_room.name))
                location.msg_contents("A new room appears {C%s{n." % (exitname), exclude=caller)

            # Set positional data, if available.
            if location.db.x != None and location.db.y != None and location.db.z != None:
                new_x, new_y, new_z = location.get_nearby_coordinates(direction)
                new_room.db.x = new_x
                new_room.db.y = new_y
                new_room.db.z = new_z


        # Create exit to the new room from the current one
        typeclass = settings.BASE_EXIT_TYPECLASS
        new_to_exit = create.create_object(typeclass,
                                           exitname,
                                           location,
                                           aliases=exitshort,
                                           locks=lockstring,
                                           destination=new_room,
                                           report_to=caller)            


        # Create exit back from new room
        new_back_exit = create.create_object(typeclass,
                                           backexitname,
                                           new_room,
                                           aliases=backexitshort,
                                           locks=lockstring,
                                           destination=location,
                                           report_to=caller)

        
        #caller.move_to(new_room)