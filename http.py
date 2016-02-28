from twisted.internet import reactor
from httpserver import *
from httpresource import Directory

if __name__ == '__main__':
    factory = SwitchFactory()
    factory.AddErrorPage(404, '404.html')
    factory.AddErrorPage(500, '500.html')
    factory.RegisterResource(Directory('html/'), '/')
    reactor.listenTCP(81, factory)
    reactor.run()
