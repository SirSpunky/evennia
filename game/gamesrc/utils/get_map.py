# -*- coding: utf-8 -*-

import traceback
import os
import datetime
import time
import sys
import django
import twisted
from time import time as timemeasure

import ev
from django.conf import settings
from src.server.caches import get_cache_sizes
from src.server.sessionhandler import SESSIONS
from src.scripts.models import ScriptDB
from src.objects.models import ObjectDB
from src.players.models import PlayerDB
from src.utils import logger, utils, gametime, create, is_pypy, prettytable, search
from src.utils.utils import crop
from src.commands.default.muxcommand import MuxCommand


def get_map(caller, map_size_x, map_size_y, show_all_rooms=False):
    caller_x = caller.location.db.x
    caller_y = caller.location.db.y
    caller_z = caller.location.db.z
    
    # Define map boundaries
    map_right_x = caller_x + (map_size_x-1)/2
    map_left_x = map_right_x - (map_size_x - 1)
    map_bottom_y = caller_y - (map_size_y-1)/2
    map_top_y = map_bottom_y + (map_size_y - 1)
    padding_left = ' '
    
    # Only show map if we know where the caller is.
    if caller_x == None or caller_y == None or caller_z == None:
        return ''
    
    # Find global script
    script_key = "GlobalDatabase"
    script = ev.search_script(script_key)
    if not script:
        self.caller.msg("Global script by name '%s' could not be found." % script_key)
        return ''
    script = script[0] # all ev.search_* methods always return lists
    
    # Prepare room cache
    if not script.ndb.cached_rooms:
        script.ndb.cached_rooms = {}
    
    if not caller.db._explored_rooms:
        caller.db._explored_rooms = {}
    
    # Create output.
    empty_row = '  ' * map_size_x + ' '
    rows = []
    for i in range(map_size_y*2+1):
        rows.append(list(empty_row))
    
    row_count = 1
    for y in range(map_top_y, map_bottom_y-1, -1):
        
        column_count = 1
        for x in range(map_left_x, map_right_x+1, 1):
            roomkey = "%s:%s:%s" % (x, y, caller_z)
            room = None
            
            # Only look for room if we're viewing all rooms, or if caller has explored this location.
            if show_all_rooms or roomkey in caller.db._explored_rooms:
                if roomkey in script.ndb.cached_rooms:
                    room = script.ndb.cached_rooms[roomkey]
                else:
                    room = caller.search(roomkey, attribute_name="xyz", typeclass="game.gamesrc.objects.room.Room", global_search=True, exact=True, quiet=True)
                    
                    if room:
                        room = room[0]
                        script.ndb.cached_rooms[roomkey] = room # Cache room so we don't have to search it again
                    else:
                        script.ndb.cached_rooms[roomkey] = None # Also cache empty hits, so we don't have to search for it again
            
            if room:
                exits = room.get_exits()
                
                # Room symbol
                room_symbol = 'o' # Default room symbol
                
                if 'u' in exits and 'd' in exits:
                    room_symbol = 'b'
                elif 'u' in exits:
                    room_symbol = 'u'
                elif 'd' in exits:
                    room_symbol = 'd'
                
                # Room color
                if room == caller.location: # If room is player's current position
                    room_symbol = '{m%s{n' % room_symbol
                elif room.tags.get("outdoors"): # If room is tagged as "outdoors".
                    room_symbol = '{g%s{n' % room_symbol
                else:
                    room_symbol = '{x%s{n' % room_symbol
                
                # Draw room
                rows[row_count][column_count] = room_symbol
                
                # Draw east exit
                if 'e' in exits:
                    rows[row_count][column_count+1] = '-'
                
                # Draw south exit
                if 's' in exits:
                    rows[row_count+1][column_count] = '|'
                
                # Draw west exit
                if 'w' in exits:
                    rows[row_count][column_count-1] = '-'
                
                # Draw north exit
                if 'n' in exits:
                    rows[row_count-1][column_count] = '|'

            column_count += 2
        row_count += 2
    
    rows = ["".join(row) for row in rows]
    
    # Strip empty top rows
    while rows[0] == empty_row:
        del rows[0]
    
    # Strip empty bottom rows
    while rows[len(rows)-1] == empty_row:
        del rows[len(rows)-1]
    
    # Join all rows with line breaks, add padding and output to caller.
    output = '\n'.join(padding_left + row for row in rows)
    
    return output