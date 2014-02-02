# -*- coding: utf-8 -*-
"""

Template for Objects

Copy this module up one level and name it as you like, then
use it as a template to create your own Objects.

To make the default commands default to creating objects of your new
type (and also change the "fallback" object used when typeclass
creation fails), change settings.BASE_OBJECT_TYPECLASS to point to
your new class, e.g.

settings.BASE_OBJECT_TYPECLASS = "game.gamesrc.objects.myobj.MyObj"

Note that objects already created in the database will not notice
this change, you have to convert them manually e.g. with the
@typeclass command.

"""
from ev import Object as DefaultObject
from ev import utils
import ev

#from game.gamesrc.commands.cmdset import MinimumCommands

class Object(DefaultObject):
    #def at_init(self):
    #    """
    #    This is always called whenever this object is initiated --
    #    that is, whenever it its typeclass is cached from memory. This
    #    happens on-demand first time the object is used or activated
    #    in some way after being created but also after each server
    #    restart or reload.
    #    """
    #
    #    #self.cmdset.add_default(MinimumCommands, permanent=True)
    #    #self.cmdset.delete(MinimumCommands)


    #------------------- Looking -------------------#
    def return_appearance(self, pobject):
        """
        This is a convenient hook for a 'look'
        command to call.
        """
        from game.gamesrc.objects.character import Character
        from game.gamesrc.objects.exit import Exit
        from game.gamesrc.objects.room import Room
        from game.gamesrc.utils.get_map import get_map
        
        # Only for exits:
        if self.destination:
            string = "\nYou peek " + self.key + ", and see..."
            string += self.destination.return_appearance(pobject)
            return string
        
        if not pobject:
            return
        
        # Name
        string = "%s" % (self.name_upper)
        
        # Name suffix for open/close and container
        if not isinstance(self, Character):
            if self.can_open:
                if self.is_open:
                    if self.is_container:
                        string += " (open)" # (open container)
                    else:
                        string += " (open)"
                else:
                    if self.is_container:
                        string += " (closed)" # (closed container)
                    else:
                        string += " (closed)"
            elif self.is_container:
                string += " (container)"
        
        
        
        # Description
        desc = self.db.desc
        if desc:
            if isinstance(self, Room):
                string += "\n"
            string += "\n%s" % desc
        
        
        
        # Room
        if isinstance(self, Room):
            # Draw mini-map.
            string += "\n\n" + get_map(pobject, 10, 5)
            
            # For debugging pathfinding
            #from game.gamesrc.utils.get_path import get_path
            #string += "\n\n" + ", ".join(get_path(self, ev.search_object("#78")[0]))
            
            # Get and identify all visible containing objects
            visible_contents = (con for con in self.contents if con != pobject and
                                                        con.access(pobject, "view"))
            exits, characters, objects = [], [], []
            
            for obj in visible_contents:
                if isinstance(obj, Exit):
                    # Add exit direction and name of destination room
                    exit_desc = obj.name_upper + " {x-{n " + obj.destination.key[0].upper() + obj.destination.key[1:]
                    
                    # Description for open/close
                    if obj.can_open:
                        if obj.is_open:
                            exit_desc += " (open)"
                        else:
                            exit_desc += " (closed)"

                    if not obj.can_open or (obj.can_open and obj.is_open):
                        # Append all characters in the destination room
                        chars_in_exit = []
                        for content in obj.destination.contents:
                            if isinstance(content, Character):
                                chars_in_exit.append(content.name)
                        if len(chars_in_exit) > 0:
                            exit_desc += " {x({n" + ", ".join(sorted(chars_in_exit)) + "{x){n"
                    
                    exits.append(exit_desc)
                elif isinstance(obj, Character):
                    characters.append(obj.name)
                else:
                    objects.append(obj.name)
                    #things.append("%cy" + key[0].upper() + key[1:] + "{n")
            
            # Draw exits
            if exits:
                #string += "\n\n{wExits: {n" + ", ".join(sorted(exits))
                #string += "\n\n{wExits:\n {n" + "\n ".join(sorted(exits))
                string += "\n\n{n" + "\n".join(sorted(exits))
            
            # Draw objects/characters
            if characters or objects:
                string += "\n\n" + ", ".join(sorted(characters) + sorted(objects))
            
        # Normal objects
        elif not isinstance(self, Character):
            # Description for open/close
            if self.can_open:
                if not self.is_open:
                    string += "\n\nIt's closed."
            
            # Append contents
            if self.is_container and self.is_open:
                contents = []
                for obj in self.contents:
                    contents.append(obj.name)
    
                if contents:
                    string += "\n\nIt contains {w%g{n of {w%g kg{n:\n" % (self.contents_weight, self.max_contents_weight)
                    string += self.return_contents() #"\n ".join(sorted(contents))
                else:
                    string += "\n\nIt's empty. It can fit {w%g kg{n." % self.max_contents_weight

        # Draw weight
        if self.own_weight > 0:
            if self.is_container:
                string += "\n\nTotal weight: {w%g kg{n" % self.total_weight
            else:
                string += "\n\nWeight: {w%g kg{n" % self.total_weight

        
        return string
    
    # Returns a formatted table of all contents in this object
    def return_contents(self):
        from src.utils import utils, prettytable
        
        table = prettytable.PrettyTable(["name", "desc", "weight"])
        table.header = False
        table.border = False
        for item in self.contents:
            name = "{C%s{n" % item.name
            if item.can_open:
                if item.is_open:
                    name += " {w(open){n"
                else:
                    name += " {w(closed){n"
            table.add_row([name, item.db.desc, "{w%g kg{n" % item.total_weight])
        
        return unicode(table)

    
    def msg(self, text=None, from_obj=None, sessid=None, **kwargs):
        """
        Emits something to any sessions attached to the object.

        message (str): The message to send
        from_obj (obj): object that is sending.
        data (object): an optional data object that may or may not
                       be used by the protocol.
        sessid: optional session target. If sessid=0, the session will
                default to self.sessid or from_obj.sessid.
        """
        if self.has_player:
            #suffix = "\n\n[ HP 100%  SP 100% ]"
            suffix = "\n\n>"
            #suffix = "\n\n{x>{n"
            #self.dbobj.msg(text=unicode(text.encode('utf-8'))+suffix, **kwargs)
            self.dbobj.msg(text=text + suffix, **kwargs)
    
    
    #------------------- Scripts -------------------#
    def start_scripts(self):
        self.stop_scripts()
        if self.db.random_messages:
            from game.gamesrc.scripts.randommessage import RandomMessage
            self.scripts.add(RandomMessage)
        
        if self.db.random_movement_rate:
            from game.gamesrc.scripts.randommovement import RandomMovement
            self.scripts.add(RandomMovement)
        
        for content in self.contents:
            content.start_scripts()
    
    def stop_scripts(self):
        for script in self.scripts.all():
            script.stop()

    #------------------- Hooks -------------------#
    def at_sayto(self, caller, msg):
        if self.db.speech:
            for keyword, answer in self.db.speech.iteritems():
                if msg.lower().find(keyword.lower()) != -1:
                    return utils.delay(1, 'sayto %s = %s' % (caller.key, answer), self.execute_cmd)
        
    
    def at_after_move(self, source_location):
        if not self.db._explored_rooms:
            self.db._explored_rooms = {}
        
        self.db._explored_rooms[self.location.db.xyz] = True

        if self.has_player:
            self.execute_cmd('look') # Look around
            
        # Todo: Look through objects in room. If enemy, take action.
        # Todo: Send hook command to at_object_arrival() to all other objects in room.
    
    def at_object_arrival(self, obj):
        # Todo: If enemy, take action.
        pass
    
    #------------------- Movement -------------------#
    def find_exit_between_rooms(self, room1, room2):
        from game.gamesrc.objects.exit import Exit
        
        if not self.location:
            return None
        
        for obj in room1.exits:
            if obj.destination == room2:
                return obj
        return None

    def announce_move_from(self, destination):
        """
        Called if the move is to be announced. This is
        called while we are still standing in the old
        location.

        destination - the place we are going to.
        """
        if not self.location:
            return

        exit = self.find_exit_between_rooms(self.location, destination)
        if not exit:
            return
        
        string = "%s leaves %s." % (self.name_upper, exit.name)
        self.location.msg_contents(string, exclude=self)

    def announce_move_to(self, source_location):
        """
        Called after the move if the move was not quiet. At this
        point we are standing in the new location.

        source_location - the place we came from
        """

        name = self.name
        if not source_location and self.location.has_player:
            # This was created from nowhere and added to a player's
            # inventory; it's probably the result of a create command.
            string = "You now have %s in your possession." % name
            self.location.msg(string)
            return

        if not self.location:
            self.location.msg_contents("%s arrives." % self.name_upper, exclude=self)
            return
        
        exit = self.find_exit_between_rooms(self.location, source_location)
        if not exit:
            self.location.msg_contents("%s arrives." % self.name_upper, exclude=self)
            return
        
        if exit.key == 'up' or exit.key == 'down':
            string = "%s arrives from %s." % (self.name_upper, exit.name)
        else:
            string = "%s arrives from the %s." % (self.name_upper, exit.name)
        self.location.msg_contents(string, exclude=self)
        
        

    #------------------- Weight -------------------#
    @property
    def max_contents_weight(self):
        if not self.db.max_contents_weight:
            return 0
        else:
            return self.db.max_contents_weight

    @property
    def max_pickup_weight(self):
        # TODO: Change to strength based
        return self.max_contents_weight

    @property
    def own_weight(self):
        if not self.db.weight:
            return 0
        else:
            return self.db.weight
        
    @property
    def contents_weight(self):
        weight = 0
        for obj in self.contents:
            weight += obj.total_weight
        return weight

    @property
    def total_weight(self):
        return self.own_weight + self.contents_weight
    
    @property
    def is_container(self):
        if self.max_contents_weight > 0:
            return True
        else:
            return False

    #------------------- Open/Close -------------------#
    @property
    def can_open(self):
        if self.tags.get("can_open"):
            return True
        else:
            return False

    @property
    def is_open(self):
        if not self.can_open:
            return True
            
        return self.db.is_open
    
    def open(self, caller=None):
        from game.gamesrc.objects.exit import Exit
        self.db.is_open = True
        
        if isinstance(self, Exit):
            self.locks.add("traverse:all()")
            
            # Open oppsite exit
            opposite_exit = self.get_opposite_exit()
            if not opposite_exit.is_open:
                opposite_exit.open()
    
    def close(self, caller=None):
        from game.gamesrc.objects.exit import Exit
        self.db.is_open = False
        
        if isinstance(self, Exit):
            self.locks.add("traverse:none()")
            
            # Open oppsite exit
            opposite_exit = self.get_opposite_exit()
            if opposite_exit.is_open:
                opposite_exit.close()

    #------------------- Tags - hooks -------------------#
    def on_add_tag(self, tag):
        from game.gamesrc.objects.exit import Exit
        if tag == "can_open" and isinstance(self, Exit):
            opposite_exit = self.get_opposite_exit()
            if not opposite_exit.can_open:
                opposite_exit.tags.add("can_open")
    
    def on_remove_tag(self, tag):
        from game.gamesrc.objects.exit import Exit
        if tag == "can_open" and isinstance(self, Exit):
            self.open()
            opposite_exit = self.get_opposite_exit()
            if opposite_exit.can_open:
                opposite_exit.tags.remove("can_open")

    #------------------- Name -------------------#
    @property
    def name(self):
        return "{x" + self.key + "{n"

    @property
    def name_upper(self):
        return "{x" + self.key[0].upper() + self.key[1:] + "{n"
