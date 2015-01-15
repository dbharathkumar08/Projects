#!/bin/env python


import sys
import optparse
import subprocess
from subprocess import Popen, PIPE

#Function to parse NS-2 trace files to calculate goodput, latency and packet loss rate
def parse():

    PACKET_SIZE=1000.0
    BIT_SIZE=8.0
    WINDOW_TIME=34
    count_received=0
    count_enque=0
    total_packet_time = 0
    throughput=0
    unique_tuple=set()
    f1 = open(sys.argv[1])
    src=sys.argv[2]
    dest=sys.argv[3]

    for line in f1.readlines():
        item = line.split()
        if item[0] == 'r' and item[4] == 'tcp':
            unique_item=str(item[8] + " " + item[9] + " " + item[10] + " "+ item[11])
            if unique_item not in unique_tuple:
                unique_tuple.add(unique_item)
    #Calculates total packet time
    for lineu in unique_tuple:
        searchcmd=str('/bin/grep'+ " " + '"'+ lineu+ '"'+ " "+sys.argv[1])
        p=subprocess.Popen(searchcmd,shell=True,stdout=subprocess.PIPE)
        enque_time=0
        received_time=0
        each_packet_time=0
        for line2 in iter(p.stdout.readline,''):
            item3 = line2.split()

            if item3[0] == '+' and item3[2] == src and item3[3] == '1' and item3[9]== dest+'.0':
                enque_time = float(item3[1])
                count_enque += 1

            if item3[0] == 'r' and item3[2] == '2' and item3[3] == dest:
                received_time = float(item3[1])
                count_received += 1
                each_packet_time = received_time - enque_time

            total_packet_time += each_packet_time


    print "Total Packet Time"
    print total_packet_time
    print "Number of packets received"
    print count_received
    print "Latency"
    print total_packet_time/count_received
    print "Throughput"
    throughput=float(count_received * BIT_SIZE* PACKET_SIZE/(WINDOW_TIME))
    print throughput
    print "No of drop_packets"
    drop_packets=float(count_enque - count_received)
    print drop_packets
    print "Drop Rate"
    drop_rate=float(drop_packets/count_enque)
    print drop_rate





parse()

