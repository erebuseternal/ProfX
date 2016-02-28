from twisted.application import internet, service
from profx import *
from profx.httpresource import Directory
application = service.Application('http')
factory = SwitchFactory()
factory.AddErrorPage(404, 'html/404.html')
factory.AddErrorPage(500, 'html/500.html')
factory.RegisterResource(Directory('html/'), '/')
staticService = internet.TCPServer(80, factory)
staticService.setServiceParent(application)
