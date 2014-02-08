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
import random
import ev
import time

from ev import Object as DefaultObject
from ev import utils

from game.gamesrc.utils.delay import delay

#from game.gamesrc.commands.cmdset import MinimumCommands

class Object(DefaultObject):

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
        self.ndb.script_session = time.time() # Script session is set to current time.
        
        if not self.location:
            return
        
        has_script = False
        
        if self.db.random_message_interval and self.db.random_messages:
            try: # Interval is an int
                delay(self.db.random_message_interval + random.random() * self.db.random_message_interval, self.repeated_message, self.ndb.script_session)
            except TypeError: # Interval is a list of min and max range
                delay(self.db.random_message_interval[0] + random.random() * self.db.random_message_interval[1] + random.random() * self.db.random_message_interval[0], self.repeated_message, self.ndb.script_session)
            has_script = True
        
        if self.db.random_movement_interval:
            try: # Interval is an int
                delay(self.db.random_movement_interval + random.random() * self.db.random_movement_interval, self.repeated_move, self.ndb.script_session)
            except TypeError: # Interval is a list of min and max range
                delay(self.db.random_movement_interval[0] + random.random() * self.db.random_movement_interval[1] + random.random() * self.db.random_movement_interval[0], self.repeated_move, self.ndb.script_session)
            has_script = True
        
        self.db._has_script = has_script
    
    def stop_scripts(self):
        self.ndb.script_session = None # Script session set to None so that all future scripts will be stopped.
    
    def repeated_move(self, script_session):
        if self.ndb.script_session != script_session:
            return # Script session is no longer valid. Abort script.
        
        self.move_in_random_direction()
        
        # Repeat
        if self.db.random_movement_interval:
            try: # Interval is an int
                delay(self.db.random_movement_interval, self.repeated_move, self.ndb.script_session)
            except TypeError: # Interval is a list of min and max range
                delay(self.db.random_movement_interval[0] + random.random() * self.db.random_movement_interval[1], self.repeated_move, self.ndb.script_session)

    def repeated_message(self, script_session):
        if self.ndb.script_session != script_session:
            return # Script session is no longer valid. Abort script.
        
        self.show_random_message(self.db.random_messages)
        
        # Repeat
        if self.db.random_message_interval and self.db.random_message_interval:
            try: # Interval is an int
                delay(self.db.random_message_interval, self.repeated_message, self.ndb.script_session)
            except TypeError: # Interval is a list of min and max range
                delay(self.db.random_message_interval[0] + random.random() * self.db.random_message_interval[1], self.repeated_message, self.ndb.script_session)

    # Move in random direction
    def move_in_random_direction(self):        
        if not self.location:
            return
        
        from game.gamesrc.objects.exit import Exit

        all_exits = []
        valid_exits = []
        
        # Required tags can be either a tag name or a list of tag names.
        required_tags = self.db.random_movement_constraint if not isinstance(self.db.random_movement_constraint, basestring) else [self.db.random_movement_constraint]
        
        for obj in self.location.exits:
            if obj.is_open:
                all_exits.append(obj)
                
                # Add to valid exits if we have no required tags, of if destination room has at least one of these tags.
                if not required_tags or any(tag in obj.destination.tags.all() for tag in required_tags):
                    valid_exits.append(obj)
        
        # If there are no valid exits, we choose from all exits.
        if len(valid_exits) == 0:
            valid_exits = all_exits
        
        if len(valid_exits) > 0:
            # Pick random room from valid exits and move to it.
            rand = int(random.random() * len(valid_exits))
            self.move_to(valid_exits[rand].destination)
            return
        

    # Return a random message
    def show_random_message(self, messages):
        if len(messages) == 0:
            return
        
        chance_per_message = 1.0/len(messages)
        
        i = 0
        for msg in messages:
            i += 1
            if random.random() <= i*chance_per_message:
                # $random_character is replaced with random character in room, excluding caller, if one is available.
                if msg.find('$random_character') != -1:
                    from game.gamesrc.objects.character import Character
                    chars = []
                    for obj in self.location.contents:
                        if isinstance(obj, Character) and obj != self:
                            chars.append(obj)
                    if len(chars) == 0:
                        return # If no chars were found, skip message.
                    r = int(random.random() * len(chars))
                    random_char = chars[r]
                    msg = msg.replace("$random_character", random_char.name);
                
                # Prefix string with "/" to execute command instead of displaying message.
                if msg[0] == "/":
                    self.execute_cmd(msg[1:])
                else:
                    if self.location:
                        self.location.msg_contents(msg)
                    else:
                        self.msg_contents(msg)
                return

    
    
    #------------------- Hooks -------------------#
    def at_sayto(self, caller, msg):
        if self.db.speech:
            for keyword, answer in self.db.speech.iteritems():
                if msg.lower().find(keyword.lower()) != -1:
                    return delay(1, self.execute_cmd, 'sayto %s = %s' % (caller.key, answer))
        
    
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
    #def travel_to(target_room, interval):
        # Travel to <target_room> using pathfinding. Wait <interval> seconds between each movement.
    #    self.db._travel_to_room = target_room
    #    self.db._travel_to_interval = interval
    
    
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
        

        
    #------------------- Melee combat -------------------#
    @property
    def reaction_time(self): # In seconds. Should be calculated from agility. Used when responding to actions, e.g. following a fleeing enemy.
        return 1
    
    def attack(self, target):
        if not self.location == target.location:
            return
        
        # If we're still recovering, wait additional time.
        #if self.ndb.recovery_time:
        #    utils.delay(self.ndb.recovery_time, target, self.attack)
        #    return False

        # Set current target
        if self.ndb.current_target != target:
            self.ndb.current_target = target
        
        # Make attack
        self.msg('You swing your fist at %s.' % (target.name))
        target.msg('%s swings %s fist at you.' % (self.name_upper, self.his))
        self.ndb.recovery_time = 10
        
        # Let enemy react
        utils.delay(target.reaction_time, self, target.at_is_attacked)
        
        # Prepare next auto-attack
        utils.delay(self.ndb.recovery_time, target, self.attack)
        return True
    
    # Hook for when object is attacked by another object.
    def at_is_attacked(self, attacker):
        if self.ndb.current_target != attacker:
            self.attack(attacker)
    
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

    
    #------------------- Gender grammatics -------------------#
    @property
    def he(self):
        if self.db.gender == 'male':
            return 'he'
        elif self.db.gender == 'female':
            return 'she'
        else:
            return 'it'
        
    @property
    def his(self):
        if self.db.gender == 'male':
            return 'his'
        elif self.db.gender == 'female':
            return 'her'
        else:
            return 'its'
    
    @property
    def him(self):
        if self.db.gender == 'male':
            return 'him'
        elif self.db.gender == 'female':
            return 'her'
        else:
            return 'it'

    @property
    def himself(self):
        if self.db.gender == 'male':
            return 'himself'
        elif self.db.gender == 'female':
            return 'herself'
        else:
            return 'itself'