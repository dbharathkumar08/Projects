__author__ = 'Bharath Kumar D'
#!/usr/bin/python
import socket
from bs4 import BeautifulSoup
import sys
from collections import deque


hostname = 'cs5700f14.ccs.neu.edu'
port = 80
global_session_id=''
crawlLink='/fakebook/'
loc = ''


def GET1():

    initial_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    initial_socket.connect((hostname , port))
    request_message = 'GET /accounts/login/?next=/fakebook/ HTTP/1.0\r\n\r\n'
    initial_socket.sendall(request_message)
    response = initial_socket.recv(4096)
    x = response.find('csrftoken=')
    y = response.find(';', x)
    csrftoken = response[x+10:y]
    p = response.find('sessionid=')
    q = response.find(';', p)
    sessionid = response[p+10:q]
    initial_socket.close()
    return (sessionid, csrftoken)

def POST():
    sessionid,csrftoken=GET1()
    input_username=sys.argv[1]
    input_password=sys.argv[2]
    post_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    post_socket.connect((hostname , port))
    post_message ='POST /accounts/login/ HTTP/1.0\r\n'
    post_message1 ='Host: cs5700f14.ccs.neu.edu\r\n'
    post_message2 ='Cookie: csrftoken='+ csrftoken +'; sessionid='+ sessionid +'\r\n'
    post_message3 ='Content-Length: 109\r\n'
    post_message4 ='Content-Type: application/x-www-form-urlencoded\r\n\r\n'
    post_message5 ='username='+input_username+'&password='+input_password+'&csrfmiddlewaretoken='+ csrftoken + '&next=%2Ffakebook%2F\r\n'
    post_socket.sendall(post_message)
    post_socket.sendall(post_message1)
    post_socket.sendall(post_message2)
    post_socket.sendall(post_message3)
    post_socket.sendall(post_message4)
    post_socket.sendall(post_message5)
    post_response = post_socket.recv(4096)

    m = post_response.find('Location:')
    k = post_response[m+9:m+48]
    loc = k
    p1 = post_response.find('sessionid=')
    q1 = post_response.find(';', p1)
    r1 = post_response[p1+10:q1]
    global global_session_id
    global_session_id = r1

    post_socket.close()


def GET():
    second_get_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    second_get_socket.connect((hostname , port))
    get_message = 'GET '+loc.strip()+' HTTP/1.0\r\n'
    #mes7 ='GET /fakebook/ HTTP/1.0\r\n'
    get_message1 ='Host: cs5700f14.ccs.neu.edu\r\n'
    global global_session_id
    get_message2 ='Cookie: sessionid='+ global_session_id +'\r\n\r\n'
    second_get_socket.sendall(get_message)
    second_get_socket.sendall(get_message1)
    second_get_socket.sendall(get_message2)
    get_response = second_get_socket.recv(4096)
    second_get_socket.close()
    return get_response


def Check_get_code(get_further_response,crawlLink):
    rep3 = get_further_response.split()
    if 301 == rep3[1]:
        a1=get_further_response.find('Location: ')
        b1 = get_further_response[a1+9:a1+48]
        if '/fakebook/' in b1:
            print "301 response"+b1
            get_further(b1)
    if 302 == rep3[1]:
        d1=get_further_response.find('Location: ')
        e1 = get_further_response[d1+9:d1+48]
        if '/fakebook/' in e1:
            print "301 response"+e1
            get_further(e1)
    if 500 == rep3[1]:
        get_further(crawlLink)
        print "500 response"+crawlLink



def get_further(crawlLink):
    final_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    final_socket.connect((hostname , port))
    get_further_message ='GET '+crawlLink.strip()+' HTTP/1.0\r\n'
    get_further_message1 ='Host: cs5700f14.ccs.neu.edu\r\n'
    global global_session_id
    get_further_message2 ='Cookie: sessionid='+ global_session_id +'\r\n\r\n'
    final_socket.sendall(get_further_message)
    final_socket.sendall(get_further_message1)
    final_socket.sendall(get_further_message2)
    get_further_response = final_socket.recv(4096)
    Check_get_code(get_further_response,crawlLink)

    return get_further_response
    final_socket.close()

def extractFlag(page):
    p1 = page.find('<h2 class=\'secret_flag\' style="color:red">FLAG: ')
    secret_flag = page[p1+48:p1+112]
    print secret_flag



def getstarted():
    if len(sys.argv) != 3:
        print "Wrong in the number of parameters"
    else:
        POST ()
        get_further_response=GET()
        soup = BeautifulSoup(get_further_response)
        result = 0
        b='/fakebook/'
        dic={}
        que = deque([b])
        while True:
            crawlLink = que.popleft()
            if crawlLink not in dic.keys():
                if '/fakebook/' in crawlLink:
                    get_further_response = get_further(crawlLink)
                    soup = BeautifulSoup(get_further_response)
                    for url in soup.find_all('a',href=True):
                        que.append((url['href']))
                    dic[crawlLink]=True
                    if '<h2 class=\'secret_flag\'' in get_further_response:
                        extractFlag(get_further_response)
                        result+=1
                    if result == 5:
                        break

getstarted()
