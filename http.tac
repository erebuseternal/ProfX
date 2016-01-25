from twisted.application import internet, service
from httpserver import *
application = service.Application('http')
factory = SwitchFactory('/root/Vision/Twisted/html/')
factory.AddErrorPage(404, '404.html')
factory.RegisterResource(Directory('/root/Vision/Twisted/html/'), '/')
staticService = internet.TCPServer(8000, factory)
staticService.setServiceParent(application)
