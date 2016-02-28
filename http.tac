from twisted.application import internet, service
from httpserver import *
from httpresource import Directory
application = service.Application('http')
factory = SwitchFactory()
factory.AddErrorPage(404, '404.html')
factory.AddErrorPage(500, '500.html')
factory.RegisterResource(Directory('html/'), '/')
staticService = internet.TCPServer(80, factory)
staticService.setServiceParent(application)
