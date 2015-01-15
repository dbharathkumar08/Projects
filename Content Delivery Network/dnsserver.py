#!/usr/bin/python
import threading 
import socket
import sys
import math
from struct import *
import urllib2
import subprocess
from subprocess import Popen, PIPE

#Client IP Address
CLIENT_IP=''
#dictionary to store the replica servers.
dict_replica_servers={}

if len(sys.argv) != 5:
	print "wrong number of inputs"
	sys.exit()
else:
	if sys.argv[1] != '-p' or sys.argv[3] != '-n':
		print "wrong inputs"
		sys.exit()
	else:
		if not 39999 < int(sys.argv[2]) < 65536:
			print "port number should be between 40000 and 65535"
			sys.exit()
  		else:
   			if sys.argv[4] != 'cs5700cdn.example.com':
    				print "wrong name"
      				sys.exit()

HOST = 'cs5700cdnproject.ccs.neu.edu'
PORT = int(sys.argv[2])

#Populate the replica servers
def populate_replica_servers():
    
    
    global dict_replica_servers
    
    virginia=(39.04, -77.49)
    oregon=(45.78, -119.53)
    california=(37.77, -122.42)
    ireland=(53.33,-6.25)
    frankfurt=(50.12,8.68)
    singapore=(1.29, 103.86)
    japan=(35.69, 139.69)
    australia=(-33.86, 151.21)
    brazil=(-10.00, -55.00)


    dict_replica_servers['54.174.6.90']=virginia
    dict_replica_servers['54.149.9.25']=oregon
    dict_replica_servers['54.67.86.61']=california
    dict_replica_servers['54.72.167.104']=ireland
    dict_replica_servers['54.93.182.67']=frankfurt
    dict_replica_servers['54.169.146.226']=singapore
    dict_replica_servers['54.65.104.220']=japan
    dict_replica_servers['54.66.212.131']=australia
    dict_replica_servers['54.94.156.232']=brazil

def choose_replica():
    global CLIENT_IP
    url_get='http://localhost:43456/csv/'
    url_fetch=url_get + CLIENT_IP
    reply=urllib2.urlopen(url_fetch)
    parsed_html = reply.read()
    reply1 = parsed_html.split(',')
    client_lat=reply1[8]
    client_long=reply1[9]
    return (client_lat, client_long)

    
def calculate_distance(client_lat, client_long):
	dict_result = {}
	for key, value in dict_replica_servers.items():
		distance=math.sqrt((float(client_lat)-value[0])**2 + (float(client_long)-value[1])**2)
		dict_result[key] = distance

	REPLICA_SEVER_IP=min(dict_result, key=dict_result.get)
	return REPLICA_SEVER_IP
        

#Get IP address of the server
def get_server_IP():
	
	s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s1.connect(("www.akamai.com",80))

	source_ip_addr=s1.getsockname()[0]
	
	return source_ip_addr
 
host_ip = get_server_IP()
#print host_ip

#Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#print 'Socket created'
 
#Bind socket to local host and port
try:
	sock.bind((host_ip, PORT))
except socket.error as msg:
	print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
	sys.exit()
	 
#print 'Socket bind complete'

#Constructing a response
def dns_response(query_id, flags, question, mydata, REPLICA_SEVER_IP):
	#global query_id
	#global flags
	#global question
	flags = (1 << 15) | flags
	flags = (1 << 7) | flags
	replica_ip = str(REPLICA_SEVER_IP)
	pack_header = pack('!HHHHHH', query_id, flags, question, 1, 0, 0)
	original_question = mydata[12:]
	answer = '\xc0\x0c'
	answer += '\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'
	answer += str.join('',map(lambda x: chr(int(x)), replica_ip.split('.')))


	return (pack_header + original_question + answer)

#Receive data from client
def parse_dns_request():
    while 1:
                p=subprocess.Popen('./freegeoip -silent=true -addr=":43456"', shell=True, stdout=subprocess.PIPE)
		#Receiving data from client 
		response = sock.recvfrom(1024)
                try:
                 t = threading.Thread(target=parse_dns_request_1, args=(response,))
                 t.start()
                except:
                 print "fail"

def parse_dns_request_1(response):
    
		global CLIENT_IP
                
		data = response[0]
		addr = response[1]
		client_ip_addr = addr[0]
		CLIENT_IP = client_ip_addr
		client_port = addr[1]
		#r_data = repr(data)
		#print "The received data is " + str(r_data)
		#print "The address received is " + str(addr)
		unpack_dns_data = unpack('!HHHHHH', data[0:12])
		#print unpack_dns_data
		query_id = unpack_dns_data[0]
		#print query_id
		flags = unpack_dns_data[1]
		#print flags
		question = unpack_dns_data[2]
		#print question
		answer = unpack_dns_data[3]
		#print answer
		authoritative_RR = unpack_dns_data[4]
		#print authoritative_RR
		additional_RR = unpack_dns_data[5]
		#print additional_RR

		#Unpack Header deatils
		query_response = (flags >> 15) & 1
		opcode = (flags >> 11) & 0xF
		authoritative_answer = (flags >> 10) & 1
		truncation = (flags >> 9) & 1 
		recursion_desired = (flags >> 8) & 1
		recursion_available = (flags >> 7) & 1
		z_reserved = (flags >> 4) & 0x7
		response_code = flags & 0xF

		#Finding the domain name
		initial_length = 12
		domain_name_length = ord(data[initial_length])
		domain_name = ''

		while domain_name_length != 0:
			domain_name += data[initial_length + 1: initial_length + domain_name_length +1]+'.'
			initial_length = initial_length + domain_name_length + 1
			domain_name_length = ord(data[initial_length])


		#print domain_name
		#return data
		if domain_name == 'cs5700cdn.example.com.':
			client_lat, client_long = choose_replica()
			REPLICA_SEVER_IP = calculate_distance(client_lat, client_long)
			reply = dns_response(query_id, flags, question, data, REPLICA_SEVER_IP)
			sock.sendto(reply, addr)


populate_replica_servers()
parse_dns_request()



sock.close()






