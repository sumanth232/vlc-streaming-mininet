# Copyright 2012 James McCauley
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
All odd hosts attached to s1, even hosts attached to s2

We are coding only one way, assuming there are only queues at 
switch s1, on the port s1-eth<n/2 + 1>
i.e the port connecting to switch s2

and another assumption that flows are only from left to right, 
i.e. from each odd numbered host to its next even host
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of

from pox.lib.util import dpidToStr
import pox.lib.packet as pkt

log = core.getLogger()

n = 4  # Maximum of 32 , only till 32, it is working for this topology
print 'NUMBER OF HOSTS - N =', n


class Tutorial (object):
  """
  A Tutorial object is created for each switch that connects.
  A Connection object for that switch is passed to the __init__ function.
  """
  def __init__ (self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection
  
    

    # This binds our PacketIn event listener
    connection.addListeners(self)

    # Use this table to keep track of which ethernet address is on
    # which switch port (keys are MACs, values are ports).
    self.mac_to_port = {}


  def resend_packet (self, packet_in, out_port):
    """
    Instructs the switch to resend a packet that it had sent to us.
    "packet_in" is the ofp_packet_in object the switch had sent to the
    controller due to a table-miss.
    """
    msg = of.ofp_packet_out()
    msg.data = packet_in

    # Add an action to send to the specified port
    action = of.ofp_action_output(port = out_port)
    msg.actions.append(action)

    # Send message to switch
    self.connection.send(msg)


  def act_like_hub (self, packet, packet_in):
    """
    Implement hub-like behavior -- send all packets to all ports besides
    the input port.
    """

    # We want to output to all ports -- we do that using the special
    # OFPP_ALL port as the output port.  (We could have also used
    # OFPP_FLOOD.)
    self.resend_packet(packet_in, of.OFPP_ALL)

    # Note that if we didn't get a valid buffer_id, a slightly better
    # implementation would check that we got the full data before
    # sending it (len(packet_in.data) should be == packet_in.total_len)).


  def act_like_switch (self, packet, packet_in):
    """
    Implement switch-like behavior.
    """

    """ # DELETE THIS LINE TO START WORKING ON THIS (AND THE ONE BELOW!) #

    # Here's some psuedocode to start you off implementing a learning
    # switch.  You'll need to rewrite it as real Python code.

    # Learn the port for the source MAC
    self.mac_to_port ... <add or update entry>

    if the port associated with the destination MAC of the packet is known:
      # Send packet out the associated port
      self.resend_packet(packet_in, ...)

      # Once you have the above working, try pushing a flow entry
      # instead of resending the packet (comment out the above and
      # uncomment and complete the below.)

      log.debug("Installing flow...")
      # Maybe the log statement should have source/destination/port?

      #msg = of.ofp_flow_mod()
      #
      ## Set fields to match received packet
      #msg.match = of.ofp_match.from_packet(packet)
      #
      #< Set other fields of flow_mod (timeouts? buffer_id?) >
      #
      #< Add an output action, and send -- similar to resend_packet() >

    else:
      # Flood the packet out everything but the input port
      # This part looks familiar, right?
      self.resend_packet(packet_in, of.OFPP_ALL)

    """ # DELETE THIS LINE TO START WORKING ON THIS #


  def _handle_PacketIn (self, event):
    """
    Handles packet in messages from the switch.
    """

    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp # The actual ofp_packet_in message.

    # Comment out the following line and uncomment the one after
    # when starting the exercise.
    self.act_like_hub(packet, packet_in)
    #self.act_like_switch(packet, packet_in)

s1_dpid = 0
s2_dpid = 0

def _handle_ConnectionUp (event):
  global s1_dpid, s2_dpid
  print "xxx ConnectionUp: ",dpidToStr(event.connection.dpid)
 
  #remember the connection dpid for switch
  for m in event.connection.features.ports:
    if m.name == "s1-eth1":
      s1_dpid = event.connection.dpid
      print "s1_dpid new =", s1_dpid
    elif m.name == "s2-eth1":
      s2_dpid = event.connection.dpid
      print "s2_dpid new =", s2_dpid


def forward_ARP(event, _port):
  msg = of.ofp_packet_out(data=event.ofp)
  msg.actions.append(of.ofp_action_output(port=_port))
  event.connection.send(msg)


def send_InstallFlow_msg_IPdst_match(event, _priority, nw_dst_str, _port, _queue_id=0):
  msg = of.ofp_flow_mod()
  msg.priority = _priority # Example 10
  msg.idle_timeout = 0
  msg.hard_timeout = 0
  msg.match.dl_type = 0x0800
  msg.match.nw_dst = nw_dst_str   # Eg : nw_dst_str can be "10.0.0.3"
  # msg.actions.append(of.ofp_action_output(port = 3))
  msg.actions.append(of.ofp_action_enqueue(port = _port, queue_id = _queue_id))
  event.connection.send(msg)


def _handle_PacketIn(event):
  global s1_dpid, s2_dpid, n
 
  packet=event.parsed
  print '_handle_PacketIn : event.connection.dpid =', event.connection.dpid
  

  if packet.type == packet.IP_TYPE:
    print "IP packet from {0}, {1}".format(packet.src, packet.payload)
  # elif packet.type == packet.ARP_TYPE:
    # print "ARP packet"
  # else:
    # print 'unknown TYPE - ',pkt.ETHERNET.ethernet.getNameForType(packet.type)


  ip=packet.find('ipv4')
  #print "_handle_PacketIn is called, packet.type:", packet.type, " event.connection.dpid:", event.connection.dpid
  if ip:
    print 'srcip = {0}, dstip = {1}, inport = {2}'.format(ip.srcip, ip.dstip, event.port)
  

  if event.connection.dpid==s1_dpid:
    # Handling ARP

    a=packet.find('arp')
    
    if a: 
      a_protodst_str = str(a.protodst)
      if a_protodst_str.startswith('10.0.0.'):
        i = int(a_protodst_str.split('.')[-1]) 
        if i%2==1:
          forward_ARP(event,(i+1)/2)
        else:
          forward_ARP(event,(n/2)+1)

    for i in range(n + 1)[1:]:
      if i%2==1:
        send_InstallFlow_msg_IPdst_match(event, 10, '10.0.0.{}'.format(i), (i+1)/2)
      else:
        ''' Sending through QoS queues '''
        if i%4 == 0:
          # HD flow
          send_InstallFlow_msg_IPdst_match(event, 10, '10.0.0.{}'.format(i), (n/2)+1, 2)
        else:
          # SD flow
          send_InstallFlow_msg_IPdst_match(event, 10, '10.0.0.{}'.format(i), (n/2)+1, 1)
        


  elif event.connection.dpid==s2_dpid:

    # Handling ARP
    a=packet.find('arp')

    if a: 
      a_protodst_str = str(a.protodst)
      if a_protodst_str.startswith('10.0.0.'):
        i = int(a_protodst_str.split('.')[-1]) 
        if i%2==1:
          forward_ARP(event, (n/2)+1)
        else:
          forward_ARP(event,i/2)

    
    for i in range(n + 1)[1:]:
      if i%2==1:
        send_InstallFlow_msg_IPdst_match(event, 10, '10.0.0.{}'.format(i), (n/2)+1)
      else:
        send_InstallFlow_msg_IPdst_match(event, 10, '10.0.0.{}'.format(i), i/2)
     

def _handle_PacketIn2(event):
  global s1_dpid, s2_dpid
 
  packet=event.parsed
  #print "_handle_PacketIn is called, packet.type:", packet.type, " event.connection.dpid:", event.connection.dpid
  print '_handle_PacketIn : event.connection.dpid =', event.connection.dpid
  
  a=packet.find('arp')
  # print 'a.protodst = ', a.protodst

  if event.connection.dpid==s1_dpid:
    
    # Handling ARP
    a=packet.find('arp')
    if a and a.protodst=="10.0.0.2":
      msg = of.ofp_packet_out(data=event.ofp)
      msg.actions.append(of.ofp_action_output(port=2))
      event.connection.send(msg)
      
    if a and a.protodst=="10.0.0.1":
      msg = of.ofp_packet_out(data=event.ofp)
      msg.actions.append(of.ofp_action_output(port=1))
      event.connection.send(msg)

    msg = of.ofp_flow_mod()
    msg.priority =100
    msg.idle_timeout = 0
    msg.hard_timeout = 0
    msg.match.dl_type = 0x0800
    #msg.match.nw_src = "10.0.0.1"
    msg.match.nw_dst = "10.0.0.2"
    msg.actions.append(of.ofp_action_output(port = 2))
    event.connection.send(msg)

    msg = of.ofp_flow_mod()
    msg.priority =100
    msg.idle_timeout = 0
    msg.hard_timeout = 0
    msg.match.dl_type = 0x0800
    msg.match.nw_dst = "10.0.0.1"
    msg.actions.append(of.ofp_action_output(port = 1))
    event.connection.send(msg)

    """
    packet = event.parsed # This is the parsed packet data.
    packet_in = event.ofp # The actual ofp_packet_in message.

    msg = of.ofp_packet_out()
    msg.data = packet_in
    # Add an action to send to the specified port
    action = of.ofp_action_output(port = of.OFPP_ALL)
    msg.actions.append(action)
    # Send message to switch
    event.connection.send(msg)
    """


def launch ():
  """
  Starts the component
  """
  # def start_switch (event):
  #   log.debug("Controlling %s" % (event.connection,))
  #   Tutorial(event.connection)
  # core.openflow.addListenerByName("ConnectionUp", start_switch)

  core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
  core.openflow.addListenerByName("PacketIn",_handle_PacketIn)
