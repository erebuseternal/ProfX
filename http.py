from twisted.internet import reactor
from httpserver import *

if __name__ == '__main__':
    factory = SwitchFactory()
    factory.AddErrorPage(404, '404.html')
    factory.RegisterResource(Directory('/root/Vision/Twisted/html/'), '/docs/')
    reactor.listenTCP(97, factory)
    reactor.run()
