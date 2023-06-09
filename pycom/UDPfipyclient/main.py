#the current example is a Wifi Client on a pysense 2.0 board with a fipy adapter to support wifi connections
#Notice that the following features
#1. Given a wifi configuration the device will go straight to conect it.
#2. the mission of this device is to measure the ambient light levels by the LTR329ALS01 driver 
# by means of a sensor on the pysense 2.0 board
#3. The captured data is being sent to UDP server which is listening on the port "IP.IP.IP.IP".49999
#which can be changed obviously.
#4. In order to save energy the device will be turn on each time the button on the pysense board is pressed
#and run the code in the function pycom_Client.

import machine
from machine import Pin
from pycoproc_2 import Pycoproc
from LTR329ALS01 import LTR329ALS01
from network import WLAN
import time
import socket
import ubinascii

def pycom_Client(arg):
    #initialising the py object of pysense 2.0
    py = Pycoproc()
    #initialising the sensor instance with the library LTR329ALS01
    light = LTR329ALS01(py)
    #initialising the wifi object
    wlan = WLAN(mode=WLAN.STA)
    #setting the access wifi parameters
    ssid = 'YOUR_WIFI_NETWORK'
    password = 'YOUR_PASSWORD'
    #trying to connect to given wifi network
    wlan.connect(ssid, auth=(WLAN.WPA2, password), timeout=5000)
    #after some hours of debugging this piece of code, it was found that before trying to move forward
    #it was necessary to spare a couple of seconds to the fipy adapter
    time.sleep(3)
    #now checking if the connection was possible
    if wlan.isconnected():
        print('WLAN connection succedded!')
        #informing the obtained ip configuration 
        print(wlan.ifconfig())  
        macfipy = ubinascii.hexlify(machine.unique_id(), ':').decode()
        print("Device MAC: ", macfipy)
        #setting the parameters to establish a connection with the UDP server
        dst = ("IP.IP.IP.IP", 49999)
        print("Sending message to: ",dst)
        #informing the data captured and the client ip details
        print("Data from "+ macfipy +" Light (channel Blue lux, channel Red lux): "+ str(light.light()) )
        #setting the UPP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)               
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1) 
        bufferSize = 1024
        #preparing the dataframe to send
        datalight = macfipy + " " + str(light.light())
        #sending the dataframe to the dst configuration UDP server
        s.sendto(datalight,dst)    
        #it is expected an answer from the UDP server in order to acknowledge the reception of the measures
        msgFromServer = s.recvfrom(bufferSize)
        #informing the server message
        msg = "Message from Server: {}".format(msgFromServer[0])    
        print(msg)
        #closing the socket
        s.close()        
        #giving some time before sending the signal to deep sleep
        time.sleep(1)
      
    time.sleep(2)
    #setting the trigger to wake up when anyone press the on-board pysense 2.0 button.
    machine.pin_sleep_wakeup(('P14','P14'),mode=machine.WAKEUP_ANY_HIGH,enable_pull=True)
    #now going to the bed eternally
    machine.deepsleep()

#initialising the Pin settings of the on-board pysense 2.0 button
p_in = Pin('P14', mode=Pin.IN, pull=Pin.PULL_DOWN)
#setting the calling back function to execute the pycom_client instructions each time the on-board pysense 2.0 button is pressed.
p_in.callback(Pin.IRQ_FALLING | Pin.IRQ_RISING, pycom_Client)

