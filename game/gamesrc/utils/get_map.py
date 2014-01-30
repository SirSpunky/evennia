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
from src.utils import logger, utils, gametime, create, is_pypy, prettytable
from src.utils.utils import crop
from src.commands.default.muxcommand import MuxCommand


def get_map(caller, map_size_x, map_size_y):
    caller_x = caller.location.db.x
    caller_y = caller.location.db.y
    caller_z = caller.location.db.z
    
    # Define map boundaries
    map_right_x = caller_x + (map_size_x-1)/2
    map_left_x = map_right_x - (map_size_x - 1)
    map_bottom_y = caller_y - (map_size_y-1)/2
    map_top_y = map_bottom_y + (map_size_y - 1)
    padding_x = ' '
    
    # Only show map if we know where the caller is.
    if caller_x == None or caller_y == None or caller_z == None:
        return
    
    # Find all rooms on caller's z-plane (up-and-down plane)
    rooms = caller.search(caller_z, attribute_name="z", typeclass="game.gamesrc.objects.room.Room", global_search=True, exact=True, quiet=True)
    
    # Select rooms within the map boundaries.
    visible_rooms = {}
    for room in rooms:
        if map_left_x <= room.db.x <= map_right_x and map_bottom_y <= room.db.y <= map_top_y:
            visible_rooms["%sx%s" % (room.db.x, room.db.y)] = room
    
    
    # Create output.
    rows = []
    empty_row = '  ' * map_size_x + ' '
    for y in range(map_top_y, map_bottom_y-1, -1):
        row0 = '' # Temp row to draw top-most exits.
        row1 = ''
        row2 = ''
        for x in range(map_left_x, map_right_x+1, 1):
            roomkey = "%sx%s" % (x, y)
            if roomkey in visible_rooms:
                room = visible_rooms[roomkey]
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
                    row1 += '{m%s{n' % room_symbol
                elif room.tags.get("outdoors"): # If room is tagged as "outdoors".
                    row1 += '{g%s{n' % room_symbol
                else:
                    row1 += '{x%s{n' % room_symbol
                
                # Draw east exit
                if 'e' in exits:
                    row1 += '-'
                else:
                    row1 += ' '
                
                # Draw south exit
                if 's' in exits:
                    row2 += '| '
                else:
                    row2 += '  '
                
                # Draw west exit, only if we're at the left edge of the map.
                if x == map_left_x:
                    if 'w' in exits:
                        row1 = '-' + row1
                    else:
                        row1 = ' ' + row1
                    row2 = ' ' + row2
                
                # Draw north exit, only if we're at the top edge of the map.
                if y == map_top_y:
                    if 'n' in exits:
                        row0 += '| '
                    else:
                        row0 += '  '
            else:
                row1 += '  '
                row2 += '  '
                
                # Draw west exit placeholder, only if we're at the left edge of the map.
                if x == map_left_x:
                    row1 = ' ' + row1
                    row2 = ' ' + row2
                
                # Draw north exit placeholder, only if we're at the top edge of the map.
                if y == map_top_y:
                    row0 += '  '
        
        if row0 and ' ' + row0 != empty_row:
            rows.append(padding_x + ' ' + row0)
        
        if row1 != empty_row:
            rows.append(padding_x + row1)
            rows.append(padding_x + row2)
    
    # Join all rows with line break and output to caller.
    output = '\n'.join(rows)
    return output