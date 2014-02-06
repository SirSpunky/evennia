# -*- coding: utf-8 -*-

from twisted.internet import threads, defer, reactor

def delay(delay, callback, *args, **kwargs):
    """
    Custom version of the built-in utils.delay() function.
    Supports any number of arguments for the callback function.
    """
    d = defer.Deferred()
    callb = callback or d.callback
    reactor.callLater(delay, callb, *args, **kwargs)
    return d