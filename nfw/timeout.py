'''
Simple asynchronous timeout wrapper.
'''
from twisted.internet import reactor, defer
from functools import wraps

class TimeoutError(Exception):
    """Raised when time expires in timeout decorator"""

DEFAULT_TIMEOUT = 3

def timeout(secs=DEFAULT_TIMEOUT):
    def wrap(func):
        @wraps(func)
        @defer.inlineCallbacks
        def _timeout(*args, **kwargs):
            timeoutValue = secs
            if 'timeout' in kwargs:
                timeoutArg = kwargs['timeout']
                if timeoutArg is not None:
                    timeoutValue = timeoutArg
                del kwargs['timeout']
            rawD = func(*args, **kwargs)
            if not isinstance(rawD, defer.Deferred):
                defer.returnValue(rawD)

            timeoutD = defer.Deferred()
            timesUp = reactor.callLater(timeoutValue, timeoutD.callback, None) #@UndefinedVariable

            dl = defer.DeferredList([rawD, timeoutD], fireOnOneCallback=True,
                                    fireOnOneErrback=True, consumeErrors=True)
            try:
                rawResult, _ = yield dl
            except defer.FirstError as e:
                #Only rawD should raise an exception
                assert e.index == 0
                timesUp.cancel()
                e.subFailure.raiseException()
            else:
                #Timeout
                if timeoutD.called:
                    rawD.cancel()
                    raise TimeoutError("%s seconds have expired" % timeoutValue)

            #No timeout
            timesUp.cancel()
            defer.returnValue(rawResult)
        return _timeout
    return wrap

def timeout2(secs):
    """
    Decorator to add timeout to Deferred calls
    """
    def wrap(func):
        @defer.inlineCallbacks
        def _timeout(*args, **kwargs):
            rawD = func(*args, **kwargs)
            if not isinstance(rawD, defer.Deferred):
                defer.returnValue(rawD)

            timeoutD = defer.Deferred()
            timesUp = reactor.callLater(secs, timeoutD.callback, None) #@UndefinedVariable

            dl = defer.DeferredList([rawD, timeoutD], fireOnOneCallback=True,
                                    fireOnOneErrback=True, consumeErrors=True)
            try:
                rawResult, _ = yield dl
            except defer.FirstError, e:
                #Only rawD should raise an exception
                assert e.index == 0
                timesUp.cancel()
                e.subFailure.raiseException()
            else:
                #Timeout
                if timeoutD.called:
                    rawD.cancel()
                    raise TimeoutError("%s secs have expired" % secs)

            #No timeout
            timesUp.cancel()
            defer.returnValue(rawResult)
        return _timeout
    return wrap


