# Python File httpserver.py

"""
This contains the protocol and factory for our resource based http server.
The idea is this. You register resource, address tuples with your server factory.
resources take in a request object and spit out a response object. The server
protocol is then created for each connection, creates a request object (catching
a server error if there is one), and then finds the closest resource to the requested
one in the request, and sends it to that resource by calling the resource.
It then receives the resource and pumps that back out into the network.
Simple as that.
"""

"""
We start with our protocol, called a Switch
"""

from twisted.protocols.basic import LineReceiver
from twisted.internet import threads, defer
from copy import deepcopy
import re

from .httpmessage import *
from .httpresource import ServerResource

"""
The switch class
"""

class Switch(LineReceiver):

    def __init__(self, factory):
        self.factory = factory
        self.response = None
        self.request = Request() # we initialize a new request object
                            # there will be only one request per switch

    def end(self, input):
        self.transport.loseConnection()

    def createResponseInThread(self, resource):
        # so now we will create
        # a defered where it is instantiated and then CreateResponse is called
        # passing in the request
        # by defering to a thread, we can allow our resource to call expensive
        # resources without having to worry about the rest of the server
        deferred = threads.deferToThread(resource.CreateResponse, self.request)
        # the returned response will be send here
        deferred.addCallbacks(self.sendResponse, self.sendServerError)

    def startResource(self):
        # this method finds the best resource given the path in the url of the
        # request. If nothing is found it returns a 404 Not Found response
        # if something is found it creates a defer by defering to a thread
        # and adds as a callback sendResponse which takes the response object
        # that is returned
        path = self.request.url.path
        resource = self.factory.getResource(path)
        if not resource:
            # we send back a 404 not found method
            response = Response()
            response.SetVersion(Version(1.1))
            response.SetStatus(Status(404))
            if not 404 in self.factory.error_pages:
                response.SetBody('<p>404 %s</p>' % Status(404).message)
            else:
                try:
                    file_address = self.factory.error_pages[404]
                    file = open(file_address, 'r')
                    body = file.read()
                    response.SetBody(body)
                except:
                    response.SetBody('<p>404 %s</p>' % Status(404).message)
            self.sendResponse(response)
            return
        # we now know that we have a resource class instance
        # first we must check to see if MAX_THREADS has already been met
        print(self)
        if not self.factory.thread_count >= self.factory.MAX_THREADS:
            # first we incrememnt the thread count
            self.factory.thread_count += 1
            try:
                self.createResponseInThread(resource)
            except:
                # if the above actions fail we want to make sure we don't make
                # our factory think it is using a thread it doesn't have.
                self.factory.thread_count -= 1
        else:
            # in this case all of the threads we are allowed to use have been
            # used up, so we have to create a deferred that can be called later
            # when a thread frees up.
            deferred = defer.Deferred()
            deferred.addCallbacks(self.createResponseInThread, self.sendServerError)
            # now we add this pair to our defers
            self.factory.defers.append((deferred, resource))

    def sendServerError(self, failure):
        # this method is called if an error is thrown by a resource's CreateResponse
        # it will send a server error response
        # first we free up a thread (that is obviously no longer being used)
        self.factory.thread_count -= 1
        response = Response()
        response.SetVersion(Version(1.1))
        response.SetStatus(Status(500))
        # now we look for the 500 page
        if not 500 in self.factory.error_pages:
            response.SetBody('<p>500 %s</p>' % Status(500).message)
        else:
            try:
                file_address = self.factory.error_pages[500]
                file = open(file_address, 'r')
                body = file.read()
                response.SetBody(body)
            except:
                response.SetBody('<p>500 %s</p>' % Status(500).message)
        self.sendResponse(response)

    def sendResponse(self, response):
        # check that this is a Response
        try:
            checkType(response, Response)
        except:
            # we send a server error response (we have to input None because
            # there is an input for a failure due to this method also being
            # used as a errback)
            self.sendServerError(None)
            return
        # now we can send our message
        # first we send the line parts of the response
        line = response.WriteLine()
        while line or line == '':
            self.sendLine(line)
            line = response.WriteLine()
        # now we see if there is a body
        if response.has_body:
            # we write out the body
            self.transport.write(response.body)
        # now we have to check if there are deferreds waiting to be triggered
        # or if we can actually free up a thread
        if len(self.factory.defers) > 0:
            # in this case we need to trigger a defer and remove it from the list
            deferred, resource = self.factory.defers.pop(0)
            # now we trigger the deferred
            deferred.callback(resource)
        else:
            # in this case we have freed up a thread and need to indicate that
            self.factory.thread_count -= 1
        # now we are done and can loose the connection
        self.transport.loseConnection()



    """
    So line will be top line, headers, and then the gap before a potential
    body which will come in as ''. Once that is done, we have to look
    into the headers to see if there is a body (httpmessage does that for us)
    and if there is we must go into raw mode and receive the rest of the
    data from rawDataReceived in order to grab the body. Then we reset
    the parser and create the response. Create response should close the
    connection for us
    """
    def lineReceived(self, line):
        # this will just make calls to self.request.ParseLine(line)
        # and once it sees line is None and
        self.request.ParseLine(line)
        if self.request.position == 'BODY':
            # once we get to the body we need to check if there is a BODY
            if self.request.has_body:
                # we go into raw mode to grab the body (body doesn't come through
                # lines)
                self.setRawMode()
            else:
                # we reset the request's parse line
                self.request.ParseLine(None)
                self.startResource()

    def rawDataReceived(self, data):
        self.request.SetBody(data)
        # we reset the request's parse line
        self.request.ParseLine(None)
        self.startResource()



from twisted.internet.protocol import ServerFactory

class SwitchFactory(ServerFactory):

    def __init__(self):
        self.resources = {}
        self.error_pages = {}   # the keys will be error codes and the values will
                                # be a file reference to the file containing the html
                                # you wish to display
        self.MAX_THREADS = 25   # just a default value
        self.defers = []        # to keep track of actions that are waiting to happen
        self.thread_count = 0   # to let us know how many threads have been opened

    def AddErrorPage(self, code, page_address):
        checkType(code, int)
        checkType(page_address, str)
        self.error_pages[code] = page_address

    def RegisterResource(self, resource, path):
        # first we check that resource is a ServerResource
        if not isinstance(resource, ServerResource):
            raise Issue('Input Resource %s is Not a Subclass of ServerResource' % resource)
        # then we make sure the path is a string
        checkType(path, str)
        # first we set the path on the resource
        resource.SetPath(path)
        # now we register the resource under the path
        self.resources[path] = resource

    def SetMaxThreads(self, number):
        # simply sets MAX_THREADS
        self.MAX_THREADS = number

    # we put this method here, because resources have to do with the factory
    def getResource(self, input_path):
        # this method returns the resource registered under the path that is
        # closest to the input_path, it returns that resource class
        # if nothing is found it returns none
        current_best_match = ''
        for path in self.resources:
            # if the url specifies a file or directory under the resource url
            # and if the resource_url which has been found is longer (and there
            #-fore more specific) than the last one, we save it as current best
            # match
            if path in input_path and len(path) > len(current_best_match):
                current_best_match = path
        if current_best_match in self.resources: # this is just to check we did find something, it is possible we didn't
            # then we return a copy of the resource. This keeps our server stateless
            return deepcopy(self.resources[current_best_match])
        else:
            return None # we didn't find anything

    def buildProtocol(self, addr):
        return Switch(self)
