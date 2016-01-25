# ProfX
This is a resource based HTTP server that I am creating for my project: IdeaBazaar. It is based upon Twisted 

HOW IT WORKS
As a twisted server, one works with a factory: in the case of ProfX that factory class is called SwitchFactory.
On initialization you may choose to enter a home directory for the switch factory. This is where Switches (the
protocol classes that the factory creates) will come to look for error pages to display if there is a server 
error or no resource is registered for the path that was entered by the client. You do not need to set a home
directory (the switches have a default page to display). 

If you choose to add a home directory, you can use AddErrorPage which takes a status code (an int) and a file
address (relative to the home directory) to set the page to diplayed when the switch itself needs to display that 
code. Note though that this only pertains to when the switch needs to create a response because something has gone
wrong with either searching for a resource or the resource itself. Therefore, only two pages are needed one for 404
and one for 500 codes. The former will be displayed when a url path comes in that has no registered resource. A 500
will be diplayed when an error occurs in the switch, or when an unhandled error in the resource is triggered.

Note that the default value for home directory is '', therefore you can still add an error page if you didn't set 
a home directory. The path will just have to be an absolute address. 

This server is resource based. This means that you register a resource (I'll tell you what that is in a minute) with 
a path. And when the server gets a request, it looks for the best match in paths and calls that resource to create a 
response. By best match I mean the path that is most specific to the entered path. An example:
  input path - /docs/nice/hello.html
  first path - /docs/
  second path - /docs/nice/
  third path - /index/
  
  Here the input path is best matched by the second, while the first is still a match, and third doesn't match at all
  
So if a client input the input path above, the resource registered with the second path would be used. If no match is 
found a 404 message is sent back to the client (using the error page with code 404 mentioned above, or default HTML in 
the switch).

So now, about the resources. A resource is a class inheriting from ServerResource that implements its own CreateResponse 
method. This method takes one input, a request object, and must return one output - a response object (with at least a status
line). How you create that response is completely up to you. You have access to all of the parameters of the request in the 
input request object as well as the path the resource was registered under in self.path (which is set by SwitchFactory on 
RegisterResource). Note that whatever path you input will be exactly what the Switch will use to try match to the client input 
path, and will be the value in self.path. ON THE OTHERHAND if you input /root into the spot for the home directory when 
initiating a SwitchFactory it will become /root/ whereas if you input /root/ it will stay that way. This is because in the 
case of SwitchFactory, we know you should be inputting a directory.

Finally two things should be noted. The first is that everytime a resource is used, the class instance that you input to 
the switch factory with RegisterResource(resource, path) is deepcopied before being used. Secondly, the resource's CreateResponse
method is called with a deferToThread call. Therefore you do not have to worry about your resource blocking the rest of the 
server. The first thing mentioned here keeps the server itself stateless (as it should be), and the second keeps things flowing 
and allows you to create the response you want without having to worry about blocking the whole thing up.
