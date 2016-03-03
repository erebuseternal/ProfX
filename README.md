# profx

profx is quite simply a series of classes designed to make building http
servers incredibly simple. And the way it does this is by providing you with
a few central components: a http request object, a http response object, a
http resource (more on that in a second), and then a server protocol and factory.
These objects in and of themselves are powerful, but their real power (in my
unbiased opinion) is how they fit together.

In profx everything that you do centers around implementing resources.
A resource is a special class which gets sent http request objects from your
server and generates an http response object. Your server can have one or many
of these resources and each resource is added to your server factory with a simple
method. When you add a resource, you also supply a path at the same time. This
path is very important. Here's why. Every time your server gets a request from some client
it will parse out the url's path.  It will then look through the paths that
you have entered with each resource and find the path that best matches (if
there is one), where a match is better if it is more specific. For example
if we have the url path /boston/docs/page.html and we have
resource 1 attached to the path /boston/, resource 2 attached to
the path /boston/docs/, and resource 3 attached to the path
/newyork/, then resources 1 and 2 will both match (3 won't)
but resource 2 will be chosen because its path is more specific. If
resource 2 had been attached to the path /boston/images/ it
wouldn't have matched at all and so resource 1 would have been chosen.

In this way profx allows you to create resources which create
responses however you want and attaches them to specific url paths, therefore
holding true to the nature of HTTP.

Now, for anyone who is familiar with twisted you know that there
is a resource based server factory and resource classes in twisted already.
So why have I done all of this? This brings us to the other strength of
profx. With profx, unlike twisted's
version of the same thing, within the resource class you have complete
and easy access to the entire request that you are now responding too.
This means you can look at things like cookies (which is actually the main
reason I wrote all this stuff).

So profx is a resource based server that gives you complete and
easy access to all parts of the requests you handle while also taking advantage
of the power twisted.

The Details

Open guide/guide.html in your favorite browser to get a more detailed look at profx.

Dependencies

 * twisted

Installation

Download the repository and inside it run: python setup.py install
