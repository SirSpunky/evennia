# -*- coding: utf-8 -*-

import ev
from game.gamesrc.objects.exit import Exit

# Helper function - Returns the distance in number of coordinates between start room and end room.
def get_distance(start_room, end_room):
    return abs(start_room.db.x-end_room.db.x) + abs(start_room.db.y-end_room.db.y) + abs(start_room.db.z-end_room.db.z)

# Returns a list of directions to get from start_room to end_room, in format ['e', 'w', 's', ...]
# Uses a custom A* pathfinding implementation with the Manhattan method: http://www.policyalmanac.org/games/aStarTutorial.htm
def get_path(start_room, end_room):
    short_directions = {'south': 's', 'north': 'n', 'west': 'w', 'east': 'e', 'up': 'u', 'down': 'd'}
    
    explored_rooms = [] # List of explored rooms that we have already evaluated.
    movement_cost_to_goal = get_distance(start_room, end_room)
    rooms_by_cost = {
        movement_cost_to_goal: [{'room': start_room, 'movement_cost_from_start': 0, 'movement_history': []}]
    }
    
    if movement_cost_to_goal == 0: # We're already at our destination
        return []
    
    #i = 0
    while len(rooms_by_cost) > 0 and movement_cost_to_goal > 0: # Stop if we're out of rooms (no path exists) or if we're at our goal
        # Get list of rooms with the lowest cost
        cheapest_cost = min(rooms_by_cost)
        cheapest_rooms = rooms_by_cost[cheapest_cost]
        
        # Pick first room
        current_room = cheapest_rooms[0]
        
        # Scan all exits in room
        for obj in current_room['room'].exits:
            if isinstance(obj, Exit) and not obj.destination in explored_rooms:
                # Room that this exit leads to has not been evaluated before.
                new_room = {}
                new_room['room'] = obj.destination
                new_room['movement_history'] = current_room['movement_history'] + [short_directions[obj.key]] # Save history of previous movement, plus new direction
                new_room['movement_cost_from_start'] = current_room['movement_cost_from_start'] + 1 # Add one to movement cost from previous room
                movement_cost_to_goal = get_distance(new_room['room'], end_room) # Estimated movement cost to end room. We don't need to store this.
                
                # If we end up at our goal using this exit, stop loop.
                if movement_cost_to_goal == 0:
                    break
                
                # Total cost is movement cost from start + movement cost to end room.
                total_cost = new_room['movement_cost_from_start'] + movement_cost_to_goal
                
                # Add new room sorted by its total cost
                if not total_cost in rooms_by_cost:
                    rooms_by_cost[total_cost] = []
                rooms_by_cost[total_cost].append(new_room)
        
        # We don't want to scan this room again.
        explored_rooms.append(current_room['room'])
        del cheapest_rooms[0]
        if len(cheapest_rooms) == 0:
            del rooms_by_cost[cheapest_cost]
        
        #i += 1
    
    # If we ended up at our goal, return movement history, else return empty list.
    if movement_cost_to_goal == 0:
        return new_room['movement_history']
    else:
        return []
