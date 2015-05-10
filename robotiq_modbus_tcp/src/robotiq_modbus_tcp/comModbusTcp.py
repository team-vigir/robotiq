# Software License Agreement (BSD License)
#
# Copyright (c) 2012, Robotiq, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Robotiq, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# Copyright (c) 2012, Robotiq, Inc.
# Revision $Id$



"""@package docstring
Module comModbusTcp: defines a class which communicates with Robotiq Grippers using the Modbus TCP protocol. 

The module depends on pymodbus (http://code.google.com/p/pymodbus/) for the Modbus TCP client.
"""

from pymodbus.client.sync import ModbusTcpClient
from pymodbus.register_read_message import ReadInputRegistersResponse
from pymodbus.exceptions import ConnectionException
from math import ceil
import time
import threading
import rospy

class communication:

   def __init__(self):
      self.client = None
      self.lock = threading.Lock()
      
   def connectToDevice(self, address):
      """Connection to the client - the method takes the IP address (as a string, e.g. '192.168.1.11') as an argument."""
      self.client = ModbusTcpClient(address)

   def disconnectFromDevice(self):
      """Close connection"""
      self.client.close()

   def sendCommand(self, data):   
      """Send a command to the Gripper - the method takes a list of uint8 as an argument. The meaning of each variable depends on the Gripper model (see support.robotiq.com for more details)"""
      #make sure data has an even number of elements   
      if(len(data) % 2 == 1):
         data.append(0)

      #Initiate message as an empty list
      message = []

      #Fill message by combining two bytes in one register
      for i in range(0, len(data)/2):
         message.append((data[2*i] << 8) + data[2*i+1])

      #To do!: Implement try/except
      try:
          with self.lock:
             self.client.write_registers(0, message)
      except ConnectionException as exc:
           rospy.logerr('Failed to connect to hand, is it on?: %s' % exc)

   def getStatus(self, numBytes):
      """Sends a request to read, wait for the response and returns the Gripper status. The method gets the number of bytes to read as an argument"""
      numRegs = int(ceil(numBytes/2.0))

      #To do!: Implement try/except 
      #Get status from the device
      try:
          with self.lock:
             response = self.client.read_input_registers(0, numRegs)
      except ConnectionException as exc:
          rospy.logerr('Failed to connect to hand, is it on?: %s' % exc)
          return []
      else:
          #Instantiate output as an empty list
          output = []

          #Fill the output with the bytes in the appropriate order
          for i in range(0, numRegs):
             output.append((response.getRegister(i) & 0xFF00) >> 8)
             output.append( response.getRegister(i) & 0x00FF)

          #Output the result
          return output
