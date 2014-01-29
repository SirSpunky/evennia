"""

Template module for Rooms

Copy this module up one level and name it as you like, then
use it as a template to create your own Objects.

To make the default commands (such as @dig) default to creating rooms
of your new type, change settings.BASE_ROOM_TYPECLASS to point to
your new class, e.g.

settings.BASE_ROOM_TYPECLASS = "game.gamesrc.objects.myroom.MyRoom"

Note that objects already created in the database will not notice
this change, you have to convert them manually e.g. with the
@typeclass command.

"""

#from ev import Room as DefaultRoom
import ev
from game.gamesrc.objects.object import Object


class Room(Object):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """
    """
    This is the base room object. It's just like any Object except its
    location is None.
    """
    def basetype_setup(self):
        """
        Simple setup, shown as an example
        (since default is None anyway)
        """

        super(Room, self).basetype_setup()
        self.locks.add(";".join(["get:false()",
                                 "puppet:false()"])) # would be weird to puppet a room ...
        self.location = None

    # Get x, y and z when moving in a certain direction
    def get_nearby_coordinates(self, direction):
        if self.db.x == None or self.db.y == None or self.db.z == None:
            return
        
        new_x = self.db.x
        new_y = self.db.y
        new_z = self.db.z
        
        if direction == 'e':
            new_x += 1
        elif direction == 'w':
            new_x -= 1
        elif direction == 'n':
            new_y += 1
        elif direction == 's':
            new_y -= 1
        elif direction == 'u':
            new_z += 1
        elif direction == 'd':
            new_z -= 1
        
        return (new_x, new_y, new_z)

    # Get room from x, y and z when moving in a certain direction
    def get_nearby_room(self, direction):
        pos = self.get_nearby_coordinates(direction)
        if not pos:
            return
        
        x = pos[0]
        y = pos[1]
        z = pos[2]
        
        rooms = ev.managers.objects.typeclass_search("game.gamesrc.objects.room.Room")
        
        for room in rooms:
            if room.db.x == x and room.db.y == y and room.db.z == z:
                return room
        

    def get_exits(self):
        directions = {'south': 's', 'north': 'n', 'west': 'w', 'east': 'e', 'up': 'u', 'down': 'd'}

        exits = []
        for obj in self.exits:
            if obj.key in directions:
                exits.append(directions[obj.key])
        
        return exits
    
    def has_exit(self, direction):
        from game.gamesrc.objects.exit import Exit
        
        for obj in self.contents:
            if isinstance(obj, Exit):
                if obj.key == direction:
                    return obj
        
        return False

    @property
    def name(self):
        return "{c" + self.key + "{n"
    
    @property
    def name_upper(self):
        return "{c" + self.key[0].upper() + self.key[1:] + "{n"
