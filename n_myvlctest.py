#!/usr/bin/python
"""
The very first line should be the above line of code for the program to run
No blank line allowed on Line-1
"""

'''
The code is hardcoded for the network (The IP addresses are hardcoded)

the network is shown below

if n=2,          
    h1-           -h2
       s1 ----- s2

if n=4,          
    h1-           -h2
       s1 ----- s2 
    h3-           -h4

and so on till max n

Code needs to be written to handle a more general network

The below global variables need to be set according to the experiment

'''




import sys
import time
from threading import Thread

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI

from functools import partial
from mininet.node import RemoteController
import subprocess
from os.path import isfile, join
import os

'''
Maximum of 32 hosts , working for this topology (some RAM limitations , i guess) - 
tested on a 4 GB Ubuntu 14.04 
'''
n = -1 # number of hosts
bw = 10.0  # link bandwidth in mbps (all links have the same bandwidth)
qos = 1     # 1 -> if QoS needs to be applied | 0 -> no QoS

'''
y = qos_k*x utility function for sd_flow
y = x is the utility function for hd_flow
'''
qos_k = 2 


workingDir = os.getcwd()

capture_script = join(workingDir, 'capture.sh')  # '/home/sumanth/mininetDir/capture.sh'

sd_flow_filepath = join(workingDir, 'testVideos/360x240_2mb.mp4') #'/home/sumanth/sample/360x240_2mb.mp4'
hd_flow_filepath = join(workingDir, 'testVideos/720x480_5mb.mp4') #'/home/sumanth/sample/720x480_5mb.mp4'
stream_time = 40 # wait for 40 seconds before shutting down (accomodate for the max time of a video safely)


savedStreamsDir = join(workingDir, 'savedStreams') # '/home/sumanth/teststorage/'
capturedTracesDir = join(workingDir, 'capturedTraces') # '/home/sumanth/mininetDir/capture_traces'


class SimpleTopo(Topo):
    global n
    # 2 switches and n hosts (n/2 hosts per switch), a link between 2 switches
    def __init__(self, **opts):
        Topo.__init__(self, **opts)

        # Adding switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        # 'dummy' is added to not use the zero index
        h = ['dummy'] # list of hosts


        # Adding hosts
        for i in range(n+1)[1:]:
            h.append(self.addHost('h{0}'.format(i)))
            if (i%2)==1:
                self.addLink(h[i], s1)
            else:
                self.addLink(h[i], s2)

        self.addLink(s1, s2)

def stream(src, dst, input_filename, output_filename, dstIP):
    global stream_time
    local_stream_time = stream_time * (n/2)

    # src, dst are host objects obtained from net.get('<host>')
    print 'Executing command on client %s <- %s'%(dst.name, src.name)
    client_command = 'cvlc rtp://@:5004 --sout \
        "#transcode{vcodec=h264,acodec=mpga,ab=128,channels=2,samplerate=44100}:\
        std{access=file,mux=mp4,dst=%s}" \
        --run-time %d vlc://quit &'%(output_filename, local_stream_time)
    result2 = dst.sendCmd(client_command)
    # print client_command
    # result2 = dst.cmd('sleep 5')

    # time.sleep(5)

    print 'Executing command on server %s -> %s'%(src.name, dst.name)
    server_command = 'cvlc -vvv %s --sout \
        "#transcode{vcodec=h264,acodec=mpga,ab=128,channels=2,samplerate=44100}:\
        duplicate{dst=rtp{dst=%s,port=5004,mux=ts}}"\
         --run-time %d vlc://quit'%(input_filename, dstIP, local_stream_time)
    result1 = src.sendCmd(server_command)
    # print server_command

    # print result1

    return (src, dst)

    # print 'streaming finished !!! - thread-{}'.format(threadIdx)



def vlcStream_working(net):
    # sample testing method to send a vlc video stream from host h1 to h2

    h1, h2 = net.get('h1', 'h2')

    print 'Executing command on h2'
    result2 = h2.cmd('cvlc rtp://@:5004 --sout \
        "#transcode{vcodec=h264,acodec=mpga,ab=128,channels=2,samplerate=44100}:std{access=file,mux=mp4,dst=output.mp4}" \
        --run-time 40 vlc://quit &')
    # result2 = h2.cmd('sleep 5')

    # time.sleep(5)

    print 'Executing command on h1'
    result1 = h1.cmd('cvlc -vvv test.mp4 --sout \
        "#transcode{vcodec=h264,acodec=mpga,ab=128,channels=2,samplerate=44100}:duplicate{dst=rtp{dst=10.0.0.2,port=5004,mux=ts}}" \
        --run-time 40 vlc://quit ')
    # result1 = h1.cmd('sleep 5')

    # result1wo = h1.waitOutput()


    print result1
    print result2
    print 'commands on h1, h2 done FINISHED'

def initiateCapture(h):
    '''
    Runs a capture script to initiate wireshark capture
    wireshark capture is used to obtain stats for throughput delay
    '''

    # # 'dummy' is added to not use the zero index
    # h = ['dummy'] # list of hosts

    # # Getting hosts
    # for i in range(n+1)[1:]:
    #     h.append(net.get('h%d'%i))

    for i in range((n/2)+1)[1:]:
        if i%2==1:
            inFilepath = sd_flow_filepath
        else:
            inFilepath = hd_flow_filepath
        
        outFile = inFilepath.split('/')[-1]   # gets the actual file name, from the full path name
        outFile = outFile.split('.')[0] + '_%dmb_link_'%bw + 'h%d_to_h%d_'%(2*i-1, 2*i)    + ('qos_' if qos else 'congest_') + '%dhosts'%n + '.pcap'
        outFile = join(capturedTracesDir,outFile)

        capture_time = stream_time + (n-2)*(stream_time/2)

        interface_name = 'h%d-eth0'%(2*i)

        command = 'bash %s %s %d %s'%(capture_script, outFile, capture_time, interface_name)
        h[2*i].cmd(command) # doesnt wait for the command to finish, if it is a blocking command

def getOutFilepath(inFilepath, i):
    outFile = inFilepath.split('/')[-1]   # gets the actual file name, from the full path name
    outFile = outFile.split('.')[0] + '_%dmb_link_'%bw + 'h%d_to_h%d_'%(2*i-1, 2*i)    + ('qos_' if qos else 'congest_') + '%dhosts'%n + '.mp4'
    outFile = join(savedStreamsDir,outFile)

    return outFile # returns a filepath

def vlcStream(net):
    # 'dummy' is added to not use the zero index
    h = ['dummy'] # list of hosts

    # Getting hosts
    for i in range(n+1)[1:]:
        h.append(net.get('h%d'%i))

    initiateCapture(h)

    # h1, h2, h3, h4 = net.get('h1', 'h2', 'h3', 'h4')
    # print 'h1 name =', h[1].name

    serv_cli_pairs = [] # list of tuples

    # threads = ['dummy']
    for i in range((n/2)+1)[1:]:
        # inFile = 'test.mp4'

        if i%2==1:
            inFile = sd_flow_filepath
        else:
            inFile = hd_flow_filepath


        outFile = getOutFilepath(inFile,i)

        # outFile = inFile.split('/')[-1]   # gets the actual file name, from the full path name
        # outFile = outFile.split('.')[0] + '_%dmb_link_'%bw + 'h%d_to_h%d_'%(2*i-1, 2*i)    + ('qos_' if qos else 'congest_') + '%dhosts'%n + '.mp4'
        # outFile = savedStreamsDir + outFile

        print 'outFile =', outFile

        # threadIdx = i

        # threads.append(Thread(target=stream, args=(h[2*i-1],h[2*i], inFile, outFile, '10.0.0.%d'%(2*i), threadIdx,)))
        serv_cli_pairs.append(stream(h[2*i-1],h[2*i], inFile, outFile, '10.0.0.%d'%(2*i)))

    ''' waiting for video flows to complete '''
    for src,dst in serv_cli_pairs:
        src.waitOutput()
        dst.waitOutput()
        print 'Video streaming complete from %s -> %s !!!'%(src.name, dst.name)



def applyQueues():
    '''
    create queues for QoS
    '''

    if not qos:
        print 'No QoS !'
        command = 'sudo ovs-vsctl set port s1-eth%d qos=@newqos -- \
            --id=@newqos create qos type=linux-htb other-config:max-rate=1000000000 queues:0=@q0 -- \
            --id=@q0 create Queue other-config:min-rate=%d other-config:max-rate=%d'%((n/2)+1, int(bw*(10**6)), int(bw*(10**6)))

        subprocess.call(command, shell=True)
    else:
        print 'Yes QoS !!!'
        command = 'ovs-vsctl -- set Port s1-eth%d qos=@newqos -- \
        --id=@newqos create QoS type=linux-htb other-config:max-rate=1000000000 queues=0=@q0,1=@q1,2=@q2 -- \
        --id=@q0 create Queue other-config:min-rate=%d other-config:max-rate=%d -- \
        --id=@q1 create Queue other-config:min-rate=%d other-config:max-rate=%d -- \
        --id=@q2 create Queue other-config:min-rate=%d other-config:max-rate=%d'%(
        (n/2)+1, 
        int(bw*(10**6)), int(bw*(10**6)),
        int((bw*(10**6))/(qos_k+1)), int((bw*(10**6))/(qos_k+1)), 
        int(((bw*(10**6))/(qos_k+1))*qos_k), int(((bw*(10**6))/(qos_k+1))*qos_k) )

        subprocess.call(command, shell=True)






def vlcTest():
    

    "Create network and run simple performance test"
    topo = SimpleTopo()
    net = Mininet(topo=topo,host=CPULimitedHost, link=TCLink,
    controller=partial(RemoteController, ip='127.0.0.1', port=6633))

    net.start()
    applyQueues()

    print "Testing network connectivity"
    net.pingAll()

    # CLI(net) # starts the mininet command line prompt

    vlcStream(net)
    net.stop()

def isValid_n(n):
    return n%4 == 0
    # return True

if __name__=='__main__':
    try:
        n = int(sys.argv[1])
        print 'n = ', n
        if not isValid_n(n):
            raise ValueError('n should be a multiple of 4 !!')

    except ValueError:
        # print sys.exc_info()[0]
        raise

    except:
        print 'Error : hosts_count argument not given'
        print 'sudo ./myvlctest_n.py <hosts_count>'
        sys.exit(2)

    setLogLevel('info')
    vlcTest()
