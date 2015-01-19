#!/usr/bin/python
import socket
import sys
from struct import *
import urllib2
import struct
from urlparse import urlparse
import random
import ntpath
from urlparse import urlparse

# making sequence_number and acknowledgement number global
tcp_seq_no =  454
tcp_ack_no = 0
system_port = random.randint(2000,50000)

#global ip_head
ip_id = random.randint(10000,50000)

#received ipheader and tcpheader
iph_r = 0
tcph_r = 0

#received seq number, ack num
glob_seq_num_r = 0
glob_ack_num_r = 0

#sendind seq and ack num
glob_seq_num_s = 0
glob_ack_num_s = 0

#ip identifier global
glob_ip_id = 0

#variables to extract header details from received packet and used as a incoming filter
rcvd_src_ip = 0
rcvd_dest_ip = 0
rcvd_src_port = 0
rcvd_dest_port = 0
expected_seq_num = 0

#gllobal fin flag
rcvd_flags = 0

#declaring data size globally
data_size=0

#dictionary to store the data
dict = {}

#server_file
server_file = ""

#filename where the data needs to be stored
#path is the path obtained from given url
#hostname is the hostname from given url
filename = ""
path = ""
hostname = ""

#Handling parameters
def check_argu():
    if len(sys.argv) != 2:
      print "wrong number of arguments"
      sys.exit(1)
check_argu()
url = sys.argv[1]

# adding http if it is missing in the url
def add_http():
    global url
    global hostname
    o = urlparse(url)
    if (o.scheme == ""):
       url = "http://" + url
       z = urlparse(url)
       hostname = z.netloc
       deal()
    else:
       hostname = o.netloc
       deal()
# extracting the path and filename from url
def deal ():
    global url
    global path
    global filename
    v = urlparse(url)
    if (v.path == ""):
       path = "/"
       filename = "index.html"
    else:
       path = v.path
       filename = ntpath.basename(v.path)
       if (filename == ""):
          filename = "index.html"
       else:
          filename = ntpath.basename(v.path)               

add_http()

 
#Create a raw socket
def create_send_socket():
    try: 
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        return s
    except socket.error , msg:
        print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()

def create_recv_socket():
    # Create a socket inorder to receive to the message
    try:
        s_recieve= socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        s_recieve.settimeout(180)
        return s_recieve
    except socket.timeout:
        print("Server didn't return any data for past 3 minutes")
        sys.exit()
    except socket.error , msg:
        print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
        
#send and receive raw socket global
ss = create_send_socket()
sr = create_recv_socket()

#Get the initial source and destination Ip
def Get_initial_source_destination_IP():
    global hostname
    s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s1.connect(("www.akamai.com",80))

    src_public_ip_addr=s1.getsockname()[0]
    #print 'src_public_ip_addr: ' + src_public_ip_addr
     
    #Find the destination IP address
    try:
       destination_ip_addr = socket.gethostbyname(hostname)
    except:
       print "wrong url"
       sys.exit(1)

    #print 'destination_ip_addr: ' + destination_ip_addr

    source_ip = src_public_ip_addr
    dest_ip = destination_ip_addr
    return source_ip, dest_ip

#global src ip address - my local machines
ips = Get_initial_source_destination_IP()
glob_src_ip=ips[0]
#print 'global src ip ' + glob_src_ip

#global dest ip - servers ip 
glob_dest_ip=ips[1]
#print 'gloab dest addr '+glob_dest_ip

#Function to calculate checksum
def checksum(msg):
    csum = 0
    ptr = 0
    n = len(msg)
    if n == 2:
       counter = 4
    else:
       counter = 3

    for i in range (n, 2, -2):
       counter = i
       curr = ord(msg[ptr])
       next = (ord(msg[ptr+1]) << 8)
       csum += curr + next
       ptr += 2
    
    if counter == 4:
       curr = ord(msg[ptr])
       next = (ord(msg[ptr+1]) << 8)
       csum += curr + next
    
    if counter == 3:
       csum+= ord(msg[ptr])
    csum = (csum >> 16) + (csum & 0xffff)
    csum += (csum >> 16)
    return((~csum) & 0xffff)


#IP Header create function
def create_ip_header():
        #IP  header fields
        ip_head_len = 5
        ip_version = 4
        ip_tos = 0
        ip_tot_len = 0  # kernel will fill the correct total length
        global ip_id
        ip_identifier = ip_id + 1#random.randint(10000,50000)  #Id of this packet
        ip_frag_off = 0
        ip_ttl = 255
        ip_protocol = socket.IPPROTO_TCP
        ip_checksum = 0    # kernel will fill the correct checksum
        global glob_src_ip
        global glob_dest_ip
        ip_srcip_addr = socket.inet_aton ( glob_src_ip )   
        ip_dstip_addr = socket.inet_aton ( glob_dest_ip )
     
        ip_head_len_version = (ip_version << 4) + ip_head_len
     
        # the ! in the pack format string means network order
        ip_header = pack('!BBHHHBBH4s4s' , ip_head_len_version, ip_tos, ip_tot_len, ip_identifier, ip_frag_off, ip_ttl, ip_protocol, ip_checksum, ip_srcip_addr, ip_dstip_addr)
        return ip_header


#Tcp header create function

def create_tcp_header(seq_no, ack_no, syn_flag, ack_flag, doff, fin_flag, rst_flag, psh_flag, urg_flag, user_data):
    #TCP header fields
        global tcp_seq_no
        tcp_src_port = system_port   # source port
        tcp_dst_port = 80   # destination port
        tcp_seq_no = seq_no
        tcp_ack_no = ack_no
        tcp_head_len = doff    #4 bit field, size of tcp header, 5 * 4 = 20 bytes
        #TCP flags
        tcp_fin = fin_flag
        tcp_syn = syn_flag
        tcp_rst = rst_flag
        tcp_psh = psh_flag
        tcp_ack = ack_flag
        tcp_urg = urg_flag
        tcp_receive_window = socket.htons (5840)    #   maximum allowed window size
        tcp_checksum = 0
        tcp_urg_ptr = 0
        
        tcp_head_len_unused = (tcp_head_len << 4) + 0
        tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh <<3) + (tcp_ack << 4) + (tcp_urg << 5)
     
        # the ! in the pack format string means network order
        tcp_header = pack('!HHLLBBHHH' , tcp_src_port, tcp_dst_port, tcp_seq_no, tcp_ack_no, tcp_head_len_unused, tcp_flags, tcp_receive_window, tcp_checksum, tcp_urg_ptr)
     
        #Creating pseudo tcp header fields
        global glob_src_ip
        global glob_dest_ip
        source_address = socket.inet_aton(glob_src_ip)
        dest_address = socket.inet_aton(glob_dest_ip)
        placeholder = 0
        protocol = socket.IPPROTO_TCP
        tcp_length = len(tcp_header) + len(user_data)
     
        psh = pack('!4s4sBBH' , source_address , dest_address , placeholder , protocol , tcp_length);
        psh = psh + tcp_header + user_data
     
        tcp_checksum = checksum(psh)
        #print tcp_checksum
     
        #Create the tcp header and fill it with correct checksum calculated like above
        tcp_header = pack('!HHLLBBH' , tcp_src_port, tcp_dst_port, tcp_seq_no, tcp_ack_no, tcp_head_len_unused, tcp_flags, tcp_receive_window) + pack('H' , tcp_checksum) + pack('!H' , tcp_urg_ptr)

        return tcp_header


#Extract ip header from received packet
def extract_iph(packet):
    #take first 20 characters for the ip header
    ip_header = packet[0:20]
    #now unpack them :)
    iph = unpack('!BBHHHBBH4s4s' , ip_header)
    return iph

#Extract tcp header from received packet
def extract_tcph(packet,iph_length):
    tcp_header = packet[iph_length:iph_length+20]
    #now unpack them :)
    tcph = unpack('!HHLLBBHHH' , tcp_header)
    return tcph

#Create the packet with the gven source_ip,dest_ip,seq_no,ack_no and request message
def create_packet( seq_no, ack_no, request_message, syn_flag, ack_flag, doff, fin_flag, rst_flag, psh_flag, urg_flag):
    ip_header = create_ip_header()
    tcp_header = create_tcp_header( seq_no, ack_no, syn_flag, ack_flag, doff, fin_flag, rst_flag, psh_flag, urg_flag,request_message)
    packet = ip_header + tcp_header + request_message
    return packet

#Function to receive packet
def recv_packet():
    global sr
    packet = sr.recvfrom(65565)

    global rcvd_src_ip
    global rcvd_dest_ip
    global rcvd_src_port
    global rcvd_dest_port
    #global expected_seq_num
     
    #packet string from tuple
    packet = packet[0]
    global tcph_r
    global iph_r

    #extracting ipheader
    iph_r = extract_iph(packet)
    #print "iph is " + str(iph_r)

    #extracting ip features
    ttl = iph_r[5]
    version_ihl = iph_r[0]
    version = version_ihl >> 4
    protocol = iph_r[6]
    ihl = version_ihl & 0xF
    iph_length = ihl * 4
    #src and dest ip of incoming packet
    rcvd_src_ip = socket.inet_ntoa(iph_r[8]);
    rcvd_dest_ip = socket.inet_ntoa(iph_r[9]);

    tcph_r = extract_tcph(packet,iph_length)
    #print "tcph is "+str(tcph_r)

    #src and dest port of incoming packet
    rcvd_src_port = tcph_r[0]
    rcvd_dest_port = tcph_r[1]

    doff_reserved = tcph_r[4]
    tcph_length = doff_reserved >> 4
    h_size = iph_length + tcph_length * 4
    #get data from the packet
    data = packet[h_size:]
    global server_file
    server_file = data
    global data_size
    data_size = len(data)

    #rcvd flag
    global rcvd_flags
    rcvd_flags = tcph_r[5]

    #received seq and ack is 
    global glob_seq_num_r
    global glob_ack_num_r
    glob_seq_num_r = tcph_r[2]
    glob_ack_num_r = tcph_r[3]

    global glob_seq_num_s
    global glob_ack_num_s
    glob_seq_num_s = glob_ack_num_r
    
    glob_ack_num_s = glob_seq_num_r + data_size

    #print "data is "+str(data)

    return packet

#Fucntion to receive SYN-ACK from server
def recv_packet_synack():
    global sr
    packet = sr.recvfrom(65565)

    global rcvd_src_ip
    global rcvd_dest_ip
    global rcvd_src_port
    global rcvd_dest_port
    #global expected_seq_num
     
    #packet string from tuple
    packet = packet[0]
    global tcph_r
    global iph_r

    #extracting ipheader
    iph_r = extract_iph(packet)
    #print "iph is " + str(iph_r)

    #extracting ip features
    ttl = iph_r[5]
    version_ihl = iph_r[0]
    version = version_ihl >> 4
    protocol = iph_r[6]
    ihl = version_ihl & 0xF
    iph_length = ihl * 4
    #src and dest ip of incoming packet
    rcvd_src_ip = socket.inet_ntoa(iph_r[8]);
    rcvd_dest_ip = socket.inet_ntoa(iph_r[9]);

    tcph_r = extract_tcph(packet,iph_length)
    #print "tcph is "+str(tcph_r)

    #src and dest port of incoming packet
    rcvd_src_port = tcph_r[0]
    rcvd_dest_port = tcph_r[1]

    doff_reserved = tcph_r[4]
    tcph_length = doff_reserved >> 4
    h_size = iph_length + tcph_length * 4
    #get data from the packet
    data = packet[h_size:]
    global server_file
    server_file = data
    global data_size
    data_size = len(data)

    #rcvd flag
    global rcvd_flags
    rcvd_flags = tcph_r[5]

    #received seq and ack is 
    global glob_seq_num_r
    global glob_ack_num_r
    glob_seq_num_r = tcph_r[2]
    glob_ack_num_r = tcph_r[3]

    global glob_seq_num_s
    global glob_ack_num_s
    glob_seq_num_s = glob_ack_num_r
    glob_ack_num_s = glob_seq_num_r + 1
    #seq is 3

    #print "data is "+str(data)

    return packet


#send syn to server    
def send_syn():
    global tcp_seq_no
    global tcp_ack_no
    request_message=''
    #Create Packet
    packet=create_packet( tcp_seq_no, tcp_ack_no, request_message, 1, 0, 5, 0, 0, 0, 0)
    #Send Packet
    global ss
    ss.sendto(packet, (glob_dest_ip, 0 ))
    #print "The message has been sent "
    recv_syn_ack()


#recv syn ack
def recv_syn_ack():
    global sr
    global filename
    global hostname
    global path
    rcvd_packet = recv_packet_synack()
    #print rcvd_packet
    send_ack()

#Send the ACK packet
def send_ack():
    global filename
    global hostname
    global path
    #sending ack, creating packet
    request_message = "GET " + path + " HTTP/1.0\r\n" + "Host: " + hostname + "\r\n\r\n"

    if (len (request_message)%2 != 0):
        request_message += '\n'


    #request_message="GET " + path + " HTTP/1.0\r\n"
    #print request_message
    #request_message="GET /classes/cs4700fa14/project4.php HTTP/1.0\r\n"
    #request_message="GET /classes/cs4700fa14/project4.php HTTP/1.1\r\n" + "Host: david.choffnes.com\r\n\r\n"
    global glob_seq_num_s
    global glob_ack_num_s
    packet=create_packet( glob_seq_num_s, glob_ack_num_s, request_message, 0, 1, 5, 0, 0, 1, 0)
    #Send Ack Packet
    global ss
    ss.sendto(packet, (glob_dest_ip, 0 ))
    global expected_seq_num
    expected_seq_num = glob_ack_num_s
    #print "in ack expected_seq_num whiuch is global send seq " + str(expected_seq_num)
    #print "The ack message has been sent "

#Send the ACK packet to every data chunk received from server
def send_request():
    request_message=""
    global glob_seq_num_s
    global glob_ack_num_s
    packet=create_packet( glob_seq_num_s, glob_ack_num_s, request_message, 0, 1, 5, 0, 0, 1, 0)
    #Send Ack Packet
    global ss
    ss.sendto(packet, (glob_dest_ip, 0 ))
    global expected_seq_num
    expected_seq_num = glob_ack_num_s


#Teardown the TCP connection
def teardown():
    global glob_seq_num_s
    global glob_ack_num_s
    request_message = ""
    packet=create_packet( glob_seq_num_s, glob_ack_num_s, request_message, 0, 1, 5, 1, 0, 0, 0)
    #Send Ack Packet
    global ss
    ss.sendto(packet, (glob_dest_ip, 0 ))

#Filter received packets
def get_started():
    counter = 0
    while True:
        rcvd_packet = recv_packet()
        #print rcvd_packet
        global expected_seq_num
        global rcvd_src_ip
        global rcvd_dest_ip
        global rcvd_src_port
        global rcvd_dest_port
        global glob_src_ip
        global glob_dest_ip
        global system_port
        global glob_ack_num_s
        global glob_seq_num_r
        global data_size
        global dict
        if (glob_dest_ip==rcvd_src_ip and glob_src_ip==rcvd_dest_ip and rcvd_dest_port==system_port and expected_seq_num == glob_seq_num_r and compare_checksum(rcvd_packet) and data_size>0 and glob_seq_num_r not in dict.keys()):
            global server_file
            
            #print "expected_seq_num "+ str(expected_seq_num)
            #print "rcvd seq num "+ str(glob_seq_num_r) + "\n"
            dict[glob_seq_num_r] = server_file
            send_request()
            global rcvd_flags
            val = (rcvd_flags&1)
            if (val == 1):
                teardown()
                break
            counter+=1
  
#Stripping off HTTP header
def remove_header(s):
    split = s.find('\r\n\r\n')
    if split >= 0:
         return s[split+4:]
    return s

#Collect the correct received packets and put it in a dictionary        
def print_result():
    global server_file
    global dict
    s = ""
    for k, v in sorted(dict.items()):
        s+=str(v)
    put_in_file(remove_header(s))

#Store the data in a file
def put_in_file(s):
    global filename
    f = open(filename, 'w')
    f.write(s)
    f.close()
    
#Verify the IP and TCP checksum
def compare_checksum(packet):
    iph = extract_iph(packet)
    version_ihl = iph[0]
    version = version_ihl >> 4
    ihl = version_ihl & 0xF
    iph_length = ihl * 4
    ttl = iph[5]
    protocol = iph[6]
    s_addr = socket.inet_ntoa(iph[8]);
    d_addr = socket.inet_ntoa(iph[9]);
      
    ip_checksum = checksum(packet[0:20])

    tcp_header = packet[iph_length:iph_length+20]
    tcph = unpack('!HHLLBBHHH' , tcp_header)
    source_port = tcph[0]
    dest_port = tcph[1]
    doff_reserved = tcph[4]
    
    tcp_flg = tcph[5]
    sequence = tcph[2]

    acknowledgement = tcph[3]
    tcp_checksum = tcph[7]                

    tcph_length = doff_reserved >> 4
    h_size = iph_length + tcph_length * 4
    data_size = len(packet) - h_size
    data = packet[h_size:]
    r_packed_tcp_header = pack('!HHLLBBHHH' , tcph[0], tcph[1], tcph[2], tcph[3], tcph[4], tcph[5],  tcph[6], 0, tcph[8])
      

    #Again create TCP pseudo header fields
    source_address = iph[8]
    dest_address = iph[9]
    placeholder = 0
    protocol = socket.IPPROTO_TCP
    tcp_length = len(r_packed_tcp_header) + len(data)
      
    psh = pack('!4s4sBBH' , source_address , dest_address , placeholder , protocol , tcp_length);
    psh = psh + r_packed_tcp_header + data;
    tcp_check = socket.htons(checksum(psh))

     
    if (ip_checksum == 0 and tcp_checksum == tcp_check):
        return True
    else:
        return False
    
      

#Call the functions here
##############################################################
send_syn()
get_started()
print_result()
##############################################################
