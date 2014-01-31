# -*- coding: utf-8 -*-
from django.conf import settings
from src.utils import utils, prettytable
from src.commands.default.muxcommand import MuxCommand
from src.commands.default.building import CmdTunnel as CmdTunnelDefault
from src.utils import create, utils, search
import random
import ev


class CmdGenerate(MuxCommand):
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

    key = ".generate"
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
        location = caller.location
        tunneling_bias = 0.75       # 0.75
        straightness_bias = -0.5    # -0.5
        max_exits = 3               # 3
        zonename = self.rhs
        max_rooms = 10
        
        # TEMP FIX FOR DEBUGGING: Destroy all rooms of current zone
        #if zonename:
        #    rooms = search.search_tag(zonename)
        #    #rooms = search.search_object("untitled room")
        #    if rooms:
        #        for room in rooms:
        #            #caller.execute_cmd('@destroy %s' % room.dbref)
        #            room.delete()
        #        caller.msg("Zone deleted.")
        #        return
        
        # Find global script
        script_key = "GlobalDatabase"
        script = ev.search_script(script_key)
        if not script:
            self.caller.msg("Global script by name '%s' could not be found." % script_key)
            return
        self.script = script[0] # all ev.search_* methods always return lists
        
        # Parse input
        starting_direction = None
        areakey = None
        if self.lhs:
            starting_direction = self.lhs.split(' ', 1)[0]
            if len(self.lhs.split(' ', 1)) > 1:
                areakey = self.lhs.split(' ', 1)[1]
        self.areakey = areakey
        
        if not location:
            caller.msg("You must be standing in a room to generate an area.")
            return
        
        if location.db.x == None or location.db.y == None or location.db.z == None:
            caller.msg("The room you're standing in is missing x, y and z coordinates.")
            return
    
        if not starting_direction or starting_direction not in self.directions:
            caller.msg("You can only generate areas in the following directions: %s." % ",".join(sorted(self.directions.keys())))
            return

        if not areakey:
            caller.msg("You must specify an area key to generate.")
            return
        
        if "areas" not in self.script.db.database or areakey not in self.script.db.database["areas"]:
            caller.msg("There's no area with that key defined.")
            return
        
        if not zonename:
            caller.msg("You must specify a zone name.")
            return
        
        if "tunneling_bias" in self.script.db.database["areas"][areakey]:
            tunneling_bias = self.script.db.database["areas"][areakey]["tunneling_bias"]
        else:
            caller.msg("No tunneling_bias set for area '%s', using default value: %s." % (areakey, tunneling_bias))
        
        if "straightness_bias" in self.script.db.database["areas"][areakey]:
            straightness_bias = self.script.db.database["areas"][areakey]["straightness_bias"]
        else:
            caller.msg("No straightness_bias set for area '%s', using default value: %s." % (areakey, straightness_bias))
        
        if "max_exits" in self.script.db.database["areas"][areakey]:
            max_exits = self.script.db.database["areas"][areakey]["max_exits"]
        else:
            caller.msg("No max_exits set for area '%s', using default value: %s." % (areakey, max_exits))
        
        if "max_rooms" in self.script.db.database["areas"][areakey]:
            max_rooms = self.script.db.database["areas"][areakey]["max_rooms"]
        else:
            caller.msg("No max_rooms set for area '%s', using default value: %s." % (areakey, rooms))
        
        if not "rooms" in self.script.db.database["areas"][areakey]:
            caller.msg("No rooms defined in area '%s'." % areakey)
            return
        
        # Create list of rooms to be randomized. Also validate room keys.
        self.rooms = {}
        self.random_roomkeys = []
        for key, value in self.script.db.database["areas"][areakey]["rooms"].iteritems():
            if not key in self.script.db.database["rooms"]:
                caller.msg("No room with key '%s' exists, but is included in area '%s'." % (key, areakey))
                return
            
            if not 0 < value < 1000:
                caller.msg("Invalid room rate %s for room key '%s' in area '%s'. Must be between 0-1000." % (value, key, areakey))
                return
            
            self.rooms[key] = self.script.db.database["rooms"][key]
            
            for x in range(0, int(round(value*100))):
                self.random_roomkeys.append(key)

        # TODO: Create list of sub-areas to be randomized. Also validate room keys.
        
        
        exitshort = starting_direction
        exitname, backexitshort = self.directions[exitshort]
        backexitname = self.directions[backexitshort][0]
        
        # Check if exit already exists in that direction.
        from game.gamesrc.objects.exit import Exit
        for obj in location.contents:
            if isinstance(obj, Exit) and obj.key == exitname:
                caller.msg("There's already an exit %s." % exitname)
                return

        # Check for nearby room in the direction we're digging.
        if location.get_nearby_room(starting_direction):
            caller.msg("There's already a room %s." % exitname)
            return
        
        # DEBUGGING: Performance test: Create 100 rooms in a straight line.
        #room = location
        #for i in range(0,100):
        #    room = self.create_room(starting_direction, room)
        #return
        
        # Create starting room
        starting_room = self.create_room(starting_direction, location)
        
        rooms_created = 1
        valid_rooms = []
        valid_rooms_deadend = [] # Valid rooms that have just one exits. These will be given higher weight if tunneling bias > 0.
        valid_rooms.append(starting_room)
        valid_rooms_deadend.append(starting_room)
        
        # Start random room generation
        while rooms_created < max_rooms and valid_rooms:
            # If tunneling bias = 1, only pick rooms with 1 exit ("dead-ends") to dig from. If tunneling bias = 0 or no dead-ends exist, pick room at random from all valid rooms.
            if valid_rooms_deadend and random.random() <= tunneling_bias:
                room_from = valid_rooms_deadend[int(random.random() * len(valid_rooms_deadend))]
            else:
                room_from = valid_rooms[int(random.random() * len(valid_rooms))]
            
            current_exits = room_from.get_exits()
            direction = None
            room_to = None
            
            # Only create exit from this room if is hasn't reached max number of exits.
            if len(current_exits) < max_exits and len(current_exits) < room_from.ndb.max_exits:
                # Find available directions by subtracting current exits from valid exits.
                available_directions = list(set(room_from.ndb.valid_exits) - set(current_exits))
                
                # Account for straightness bias.
                if len(current_exits) == 1:
                    if straightness_bias >= 0 and random.random() <= straightness_bias:
                        # Positive straightness bias: only let exit be created in straight (opposite) direction.
                        straight_direction = self.directions[current_exits[0]][1]
                        available_directions = [straight_direction]
                    elif straightness_bias < 0 and random.random() * -1 >= straightness_bias:
                        # Negative straightness bias: avoid opposite exits.
                        straight_direction = self.directions[current_exits[0]][1]
                        if straight_direction in available_directions:
                            available_directions.remove(straight_direction)
                
                # Keep try new directions until a valid one is found.
                while not direction and available_directions:
                    direction = available_directions[int(random.random() * len(available_directions))] # Find random direction
                    
                    room_to = room_from.get_nearby_room(direction) # Is there already a room on these coordinates?
                    if room_to:
                        # Room already exists in that direction. Can we connect to it?
                        
                        # Connect less rooms is we have a tunneling bias.
                        if random.random() <= tunneling_bias:
                            available_directions.remove(direction)
                            direction = None
                            continue
                        
                        # Only connect rooms that are valid. This excludes rooms from outside zones.
                        if not room_to in valid_rooms:
                            available_directions.remove(direction)
                            direction = None
                            continue
                        
                        # Only connect room if it doesn't already have max number of exits.
                        if len(room_to.get_exits()) >= room_to.ndb.max_exits:
                            available_directions.remove(direction)
                            direction = None
                            continue
                        
                        # Check if room is in correct zone
                        #if not room_to.tags.get(zonename, category="zone"):
                            
                            
            # If this was previously a valid dead-end, it should no longer be.
            if room_from in valid_rooms_deadend:
                valid_rooms_deadend.remove(room_from)
            
            if not direction:
                # No valid direction found, remove this room from valid rooms and look for another room.
                valid_rooms.remove(room_from)
                continue
            else:
                # Valid direction found.
                if room_to:
                    # Room already exists at direction. Only create exit to it.
                    self.create_exits(direction, room_from, room_to)
                else:
                    # No room found in direction so create a new room.
                    room_to = self.create_room(direction, room_from)
                    valid_rooms.append(room_to)
                    valid_rooms_deadend.append(room_to)
                    rooms_created += 1
        
        caller.msg("You generate a new random area {C%s{n, with area key '%s' and zone name '%s'." % (exitname, areakey, zonename))
        location.msg_contents("%s generates a new random area {C%s{n." % (caller.name, exitname), exclude=caller)



    def create_room(self, direction, room_from):
        zonename = self.rhs
        areakey = self.areakey
        roomname = "untitled room"
        desc = ""
        max_exits = 4
        valid_exits = ['n', 's', 'w', 'e']
        tags = []
        objects = {}
        limit = 0
        attr = {}
        
        # All random room generation stuff
        roomkey = self.random_roomkeys[int(random.random() * len(self.random_roomkeys))] # Find random room key
        room_data = self.rooms[roomkey]
        
        if "name" in room_data:
            if isinstance(room_data["name"], basestring):
                roomname = room_data["name"]
            else:
                roomname = room_data["name"][int(random.random() * len(room_data["name"]))] # Find random from list
        
        if "desc" in room_data:
            if isinstance(room_data["desc"], basestring):
                desc = room_data["desc"]
            else:
                desc = room_data["desc"][int(random.random() * len(room_data["desc"]))] # Find random from list
        
        if "max_exits" in room_data:
            max_exits = room_data["max_exits"]
        
        if "valid_exits" in room_data:
            valid_exits = room_data["valid_exits"]
        
        if "tags" in room_data:
            tags = room_data["tags"]
        
        if "objects" in room_data:
            objects = room_data["objects"]
        
        if "limit" in room_data:
            limit = room_data["limit"]
        
        typeclass = settings.BASE_ROOM_TYPECLASS
        lockstring = "control:id(%s) or perm(Immortals); delete:id(%s) or perm(Wizards); edit:id(%s) or perm(Wizards)"
        lockstring = lockstring % (self.caller.dbref, self.caller.dbref, self.caller.dbref)

        new_room = create.create_object(typeclass, roomname, report_to=self.caller)
        new_room.locks.add(lockstring)

        new_room.db.desc = desc
        new_room.ndb.max_exits = max_exits
        new_room.ndb.valid_exits = valid_exits

        # Set positional data.
        new_x, new_y, new_z = room_from.get_nearby_coordinates(direction)
        new_room.db.x = new_x
        new_room.db.y = new_y
        new_room.db.z = new_z
        
        
        # Default tags
        new_room.tags.add(zonename, category="zones")
        new_room.tags.add(roomkey, category="room_types")
        new_room.tags.add(areakey, category="area_types")
        # TODO: Add coordinate area tag, e.g. 0x0x1-10x10x1, to quickly match all rooms within this area. Mostly for utils.get_map
        
        # Custom tags
        for tag in tags:
            new_room.tags.add(tag)
        
        # Exits
        self.create_exits(direction, room_from, new_room)
        
        # Objects
        for object_key, chance in objects.iteritems():
            # Randomize chance of spawning object. 0 = Never. 1 = Always. Todo: 2+ = Create at least 2+ objects.
            if random.random() <= chance:
                
                # Search for object key in template database
                if object_key in self.script.db.database["template_objects"]:
                    self.create_object(object_key, new_room) # We have a match. Create it!
                    caller.msg("Created object '%s' in room '%s'." % (object_key, roomkey))
                else:
                    caller.msg("There's no object with key '%s' as defined in room '%s'." % (object_key, roomkey))
        
        return new_room
    
    def create_object(self, object_key, location):
        old_obj = self.script.db.database["template_objects"][object_key]["object"]
        
        from game.gamesrc.utils.copy_object_recursive import copy_object_recursive
        new_obj = copy_object_recursive(old_obj)
        
        # Set object location
        new_obj.home = location
        new_obj.move_to(location, quiet=True)
        
        new_obj.start_scripts()
        if new_obj.db.is_template:
            del new_obj.db.is_template
        
        return new_obj
    
    def create_exits(self, direction, room_from, room_to):
        lockstring = "control:id(%s) or perm(Immortals); delete:id(%s) or perm(Wizards); edit:id(%s) or perm(Wizards)"
        lockstring = lockstring % (self.caller.dbref, self.caller.dbref, self.caller.dbref)

        exitshort = direction
        exitname, backexitshort = self.directions[exitshort]
        backexitname = self.directions[backexitshort][0]
        
        # Create exit to the new room from the current one
        typeclass = settings.BASE_EXIT_TYPECLASS
        new_to_exit = create.create_object(typeclass,
                                           exitname,
                                           room_from,
                                           aliases=exitshort,
                                           locks=lockstring,
                                           destination=room_to,
                                           report_to=self.caller)            


        # Create exit back from new room
        new_back_exit = create.create_object(typeclass,
                                           backexitname,
                                           room_to,
                                           aliases=backexitshort,
                                           locks=lockstring,
                                           destination=room_from,
                                           report_to=self.caller)
    