The purpose of this project is to implement a web crawler that traverses through the Web and gathers five unique secret flags.
It is implemented in Python.  

This program can be executed by executing the script using the command ./webcrawler and pass the parameters to run the script.

High-level approach:
Initially, the socket connection is created. Once it is established, the HTTP request response messages are built. The value of cookies 
is extracted and sent in subsequent requests while crawling the Fakebook. For parsing the HTML, the Python library - Beautiful Soup is 
used which makes the task of parsing easier. In order to store the links and parse each one by one, we stored all the links in queue. 
A dictionary is used to store the visited links. Status codes are also handled in the specified way. In all this process, a check on 
the count of secret flags is performed and the program terminates when five secret flags are done.

Challenges:
1. We used a lot of headers while sending the HTTP request including Accept-Encoding: gzip, deflate. Due to usage of this header, the 
server responded in binary format which was not readable. Removing the unnecessay headers made the task simple. 

2. Constructing the HTTP POST request message was erroneous as we didn't handle CRLF properly.

3. While parsing the HTML using Beautiful Soup, we faced an Attribute error which occurred because we were passing the message from server 
as a string to the Beautiful Soup object instead of passing it as html. 

Testing the code:
1. While building the code, we tested every line of the code by printing it. 

2. The final code was tested by executing the script and passing different pair of usernames and passwords. 







 