#The current example is a Wifi Client on raspberry Pi Pico W board.
#Notice that the following features
#1. Given a wifi configuration the device will go straight to conect it.
#2. The mission of this device is to measure the temperature and sending the measure to a TCP server every 30s
#3. The captured data is being sent to TCP server which is listening on the port "IP.IP.IP.IP".50000
#which can be changed obviously.
#4. It seems that there is discontinuity in Timer Module support on Raspberry Pi Pico series. 
#Consequently, it was not possible to set a deep sleep feature in order to save energy. 
#This issue is still on research.

#Loading required libraries
import machine
from machine import Timer
from machine import RTC
import network
import time
import ubinascii
import socket

#defining resources
#enabling the temperature sensor
adc = machine.ADC(machine.ADC.CORE_TEMP)

#defining a shared global variable as a counter of events
count = 0
# Configure network credentials
ssid = 'xxxxx'
password = 'xxxxx'




#temperature capturing function
def temperature():
    #In order to force microython to use the global varibales adc and count, they are declared again by pointing 
    # out as global variables.   
    global adc
    global count
    
    #reading temperature
    temp = adc.read_u16() * 3.3 / 65535
    #Converting the value to an acceptable Celcius grade measure
    temp = 27 - (temp - 0.706) / 0.001721
    #impcrementing the global shared variable for testing purposes
    count +=1
    
    return temp

while True:
    #defining the wlan object
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    #showing some info for debugging purposes
    print("Connecting Process")
    #This implementation of client will scan the wifi networks in the zone
    nets = wlan.scan()
    #For each wifi netowork, it tries to match the given ssid
    for net in nets:
        
        #using the ouptut provided by wlan.scan method to search the prefered wifi network
        if net[0].decode() == ssid:
            print('Network found!')
            wlan.active(True)
            #As a best practice, it is effective to give some time before trying to engage upon the current 
            #wifi configuration detected
            time.sleep(2)
            #atempting the connection
            wlan.connect(str.encode(ssid), str.encode(password))
            #Breaking the search, if the connection. The following lines are candidate to be removed in future versions
            #because there were useful while starting the development of this script
            while not wlan.isconnected():
                    pass
            
            break
        else:
             #informing if the network was not found
             print('Network Not found!')
             break
    #Checking the Wifi Connection before any action    
    if wlan.isconnected():
        #Setting tha title
        print('WLAN connection succedded!')
        #Reporting the wifi configuration obtained
        print(wlan.ifconfig())  
        macpico = ubinascii.hexlify(machine.unique_id(), ':').decode()
        print("Device MAC: ", macpico)
        #Setting a server IP details which must customised
        dst = ("192.168.50.28", 50000)
        
        print("Sending message to: ",dst)
        
        #Handling the possible exceptions on sending the data
        try:
            #The standard instruction to set up a TCP socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            #Setting the buffer data transfer size
            bufferSize = 1024
            #Establishing the connection with server
            s.connect(dst)
            #As the deep sleep feature was unavailable
            #Setting the loop to send the temperature every certain amount of time
            while True:
                    #preparing the data frame to send
                    datatemp = macpico + " " + str(temperature())
                    #printing the result for debugging purposes.
                    print(datatemp)
                    #Executing the transmission
                    s.send(datatemp)
                    #Establishing a gap between transmission and server response
                    time.sleep(2)
                    #Receiving a server response 
                    data = s.recvfrom(1024)
                    #printing the result for debugging purposes.
                    print(data)
                    #Validating the received message
                    if not data: break
                    else:
                        #printing the result for debugging purposes.
                        print("raw server answer: ",data)
                    #Given some time before continue with the next elemento in nets
                    time.sleep(2)
        except:
            #As the connection was not possible
            print("Broken Conection")
            time.sleep(5)
            continue
        
        
        #closing the socket
        s.close()
    #closing the wifi connetion 
    wlan.disconnect()
    #Disactivating the wlan resource
    wlan.active(False)    
    #Establishing a gap between attempts
    time.sleep(20)
    
