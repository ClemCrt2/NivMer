#!/usr/bin/python3.7
import socket

msgFromClient       = "31/07/2021,05:30:00,2160,27\n"
bytesToSend         = str.encode(msgFromClient)
serverAddressPort   = ("192.168.11.208", 3035)
bufferSize          = 1024

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Send to server using created UDP socket
UDPClientSocket.sendto(bytesToSend, serverAddressPort)

#msgFromServer = UDPClientSocket.recvfrom(bufferSize)

#msg = "Message from Server {}".format(msgFromServer[0])

#print(msg)
