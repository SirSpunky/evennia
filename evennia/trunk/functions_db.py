import sets
from django.contrib.auth.models import User
from apps.objects.models import Object

def get_nextfree_dbnum():
   """
   Figure out what our next free database reference number is.
   """
   # First we'll see if there's an object of type 5 (GARBAGE) that we
   # can recycle.
   nextfree = Object.objects.filter(type__exact=5)
   if nextfree:
      # We've got at least one garbage object to recycle.
      #return nextfree.id
      return nextfree[0].id
   else:
      # No garbage to recycle, find the highest dbnum and increment it
      # for our next free.
      return Object.objects.order_by('-id')[0].id + 1

def list_search_object_namestr(searchlist, ostring, dbref_only=False):
   """
   Iterates through a list of objects and returns a list of
   name matches.
   """
   if dbref_only:
      return [prospect for prospect in searchlist if prospect.dbref_match(ostring)]
   else:
      return [prospect for prospect in searchlist if prospect.name_match(ostring)]
      
def local_and_global_search(object, ostring, local_only=False):
   """
   Searches an object's location then globally for a dbref or name match.
   local_only: Only compare the objects in the player's location if True.
   """
   search_query = ''.join(ostring)

   if is_dbref(ostring) and not local_only:
      search_num = search_query[1:]
      dbref_match = list(Object.objects.filter(id=search_num))
      if len(dbref_match) > 0:
         return dbref_match

   local_matches = list_search_object_namestr(object.location.get_contents(), search_query)
   
   # If the object the invoker is in matches, add it as well.
   if object.location.dbref_match(ostring) or ostring == 'here':
      local_matches.append(object.location)
   
   return local_matches

def is_dbref(dbstring):
   """
   Is the input a well-formed dbref number?
   """
   try:
      number = int(dbstring[1:])
   except ValueError:
      return False
   
   if dbstring[0] != '#':
      return False
   elif number < 1:
      return False
   else:
      return True
   
def session_from_object(session_list, targobject):
   """
   Return the session object given a object (if there is one open).
   """
   results = [prospect for prospect in session_list if prospect.pobject == targobject]
   if results:
      return results[0]
   else:
      return False

def session_from_dbref(session_list, dbstring):
   """
   Return the session object given a dbref (if there is one open).
   """
   if is_dbref(dbstring):
      results = [prospect for prospect in session_list if prospect.pobject.dbref_match(dbstring)]
      if results:
         return results[0]
   else:
      return False
      
def get_object_from_dbref(server, dbref):
   """
   Returns an object when given a dbref.
   """
   return server.object_list.get(dbref, False)
   
def create_user(cdat, uname, email, password):
   """
   Handles the creation of new users.
   """
   session = cdat['session']
   server = cdat['server']
   start_room = int(server.get_configvalue('player_dbnum_start'))
   start_room_obj = get_object_from_dbref(server, start_room)

   # The user's entry in the User table must match up to an object
   # on the object table. The id's are the same, we need to figure out
   # the next free unique ID to use and make sure the two entries are
   # the same number.
   uid = get_nextfree_dbnum()
   user = User.objects.create_user(uname, email, password)
   # It stinks to have to do this but it's the only trivial way now.
   user.id = uid
   user.save

   # Create a player object of the same ID in the Objects table.
   user_object = Object(id=uid, type=1, name=uname, location=start_room_obj)
   user_object.save()
   server.add_object_to_cache(user_object)

   # Activate the player's session and set them loose.
   session.login(user)
   print 'Registration: %s' % (session,)
   session.push("Welcome to %s, %s.\n\r" % (server.get_configvalue('site_name'), session.name,))