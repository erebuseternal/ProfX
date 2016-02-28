from httpmessage import *

"""
This is the base class for a resource and I will place resource implementations
here as well.
"""

"""
A server resource must have a CreateResponse method which takes a request
and returns a response object. The server switches will call CreateResponse
on the Resource that matches the url found in the request. Just look at the
Switch Class.
"""

# this is the base class for a resource, and it just echos the request object
# it should also have a path attribute which specifies the path
# it is set to be a resource under
class ServerResource:

    def SetPath(self, path):
        checkType(path, str)
        self.path = path

    def CreateResponse(self, request):
        # this request will be a request object
        # this method needs to deal with this request object and return
        # a response. I am going to make this basic class just echo
        response = Response()
        response.version = request.version
        response.status = Status(200)
        response.headers = request.headers
        response.header_names = request.header_names
        response.has_body = request.has_body
        response.body = request.body
        return response

# this is a resource that serves static content in a directory
class Directory(ServerResource):

    def __init__(self, directory):
        # directory is the directory from which it will serve things in the
        # request
        if directory[-1] != '/':
            directory = directory + '/'
        self.directory = directory

    def CreateResponse(self, request):
        # first we find the part of the url after the path this resource
        # was set under
        if self.path[-1] != '/':
            self.path = self.path + '/'
        re_expression = re.compile(self.path)
        match = re.search(re_expression, request.url.path)
        index_of_rest = match.end()
        path = request.url.path[index_of_rest:]
        if path == '':
            # we route to index.html by default
            path = 'index.html'
        try:
            file = open(self.directory + path, 'r')
        except:
            # in this case we need to send a 404
            response = Response()
            response.SetVersion(Version(1.1))
            response.SetStatus(Status(404))
            response.SetBody('<p>404 Not Found<p>')
            return response
        # okay so we got the file, so now to send it
        body = file.read()
        response = Response()
        response.SetVersion(Version(1.1))
        response.SetStatus(Status(200))
        response.SetBody(body)  # set body adds the appropriate headers for us
        return response
