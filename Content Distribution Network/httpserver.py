#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn
import threading

import urllib2
import sys
import os

#Checking the correct number of arguments passed
if len(sys.argv) == 5:
 if sys.argv[1] == '-p' and sys.argv[3] == '-o':
  if 39999 < int(sys.argv[2]) < 65536:
      print ""
  else:
    print "port number should be between 40000 and 65535"
    print sys.argv[2]
    sys.exit(1)
 else:
    print "wrong inputs"
    sys.exit(1)
else:
    print "wrong number of inputs"
    sys.exit(1)

#PORT number that has to be set
PORT = int(sys.argv[2])

#dictionary which keeps the count
#on the number of times the page was hit.
dict_count={}

#origin server
origin = sys.argv[4]


#Get the filename from the specified path
def get_filename(path):
     a=path.split('/')
     b=[origin]
     i=0
     for item in a:
      if i == len(a)-1:
        b.append(item)
      else:
        i=i+1
        b.append(item)
        b.append('_')
     #Join the list elements 
     c=''.join(b)
     filename=c+'.html'
     return filename

#Store the file in cache
def add_file(filename, webpage, path):
    global dict_count
    try:
        #Open a file to which we add the contents.
         f = open(filename, 'w')
         f.write(webpage)
         f.close()
         
    except IOError:
             #Remove the item that has the least visit count
             remove_key=min(dict_count, key=dict_count.get)
             del dict_count[remove_key]
             
             #Remove the file from the cache 
             remove_file=get_filename(remove_key)
             os.remove(remove_file)
             #Try to add the content again
             add_file(filename, webpage, path)
             
    else:
             #Set  the visit count to 1.
             dict_count[path]=1
             
#Get Request Handler
class Handler(BaseHTTPRequestHandler):

    def do_GET(s):
         #store the path
         path=s.path
         
         #Check whether the path is already in count 
         if path not in dict_count.keys():
             url_get=origin+s.path
             url_fetch='http://'+ url_get
             try:
                reply=urllib2.urlopen(url_fetch)
             except urllib2.HTTPError, e:
                 s.send_response(e.code)
                 
             else:
                 #Webpage from the GET request to the server
                 webpage= reply.read()
                 #Create the filename from the specified path
                 filename=get_filename(path)
                 #Caching the webpage
                 #Add the webpage to the file
                 add_file(filename, webpage, path)
                 s.send_response(200)
                 s.send_header('Content-type','text/html')
                 s.end_headers()
                # Send the html message
                 s.wfile.write(webpage)
         else:
             
             
             #Added if it is to fetch from file only
             filename=get_filename(path)
             f = open(filename, 'r')
             webpage=f.read()
             f.close()
             #Increment the page hit count
             dict_count[path]=dict_count[path]+1
             s.send_response(200)
             s.send_header('Content-type','text/html')
             s.end_headers()
            # Send the html message
             s.wfile.write(webpage)
             
         return
    
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Thread creation"""

try:
    server = ThreadedHTTPServer(('', PORT), Handler)  
    #Server waits forever till there is a keyboard exception
    server.serve_forever()
except KeyboardInterrupt:
    server.socket.close()
