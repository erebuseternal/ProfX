from twisted.internet import reactor
from profx import *
from profx.httpresource import Directory

if __name__ == '__main__':
    factory = SwitchFactory()
    factory.AddErrorPage(404, 'html/404.html')
    factory.AddErrorPage(500, 'html/500.html')
    factory.RegisterResource(Directory('html/'), '/')
    reactor.listenTCP(81, factory)
    reactor.run()
