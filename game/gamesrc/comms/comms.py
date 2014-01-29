"""
Default Typeclass for Comms.

See objects.objects for more information on Typeclassing.
"""
#from ev import Channel as DefaultChannel
from src.comms.comms import Channel as DefaultChannel
#from src.comms import Msg, TempMsg, ChannelDB
#from src.typeclasses.typeclass import TypeClass
#from src.utils import logger
#from src.utils.utils import make_iter


class Channel(DefaultChannel):
    """
    This is the base class for all Comms. Inherit from this to create different
    types of communication channels.
    """
    def __init__(self, dbobj):
        super(Channel, self).__init__(dbobj)