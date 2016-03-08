from twisted.application import internet, service
from twisted.internet import reactor
from __init__ import *
from httpresource import Directory
from httpmessage import Response
from time import sleep

from httpresource import ServerResource

class Wait(ServerResource):
    def CreateResponse(self, request):
        print('starting')
        sleep(5)
        print('midway')
        sleep(5)
        response = Response()
        response.SetBody('the wait is over')
        return response


application = service.Application('http')
factory = SwitchFactory()
factory.SetMaxThreads(1)
factory.RegisterResource(Wait(), '/')
reactor.listenTCP(100, factory)
reactor.run()
