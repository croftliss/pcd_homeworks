import datetime
import socket
import sys
import time
from threading import Thread

IP = "127.0.0.1"
UDP_PORT = 5000
TCP_PORT = 5001
MESSAGE_SIZE = 65535

def connectTcp():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((IP, TCP_PORT))
    sock.listen(1)
    while True:
        conn, addr = sock.accept()
        thread = Thread(target = connectionTcpHandler, args = (conn, ))
        thread.start()

def connectionTcpHandler(connection):
    bytesReceived = 0
    noMessagesReceived = 0
    try:
        totalBytes = 0
        while True:
            data = connection.recv(MESSAGE_SIZE)
            bytesReceived += len(data)
            noMessagesReceived +=1
            if not data: 
                break
            connection.send(str.encode("ACK"))
        connection.close()
    except:
        print("Problem encountered...")
    print("Protocol: TCP")
    print("Bytes Received : " + str(bytesReceived))
    print("Messages Received: " + str(noMessagesReceived))    

def connectUdp(): 
    bytesReceived = 0
    messagesReceived = 0

    clientsDict = {}
    thread = Thread(target = connectionUdpHandler, args = (clientsDict, ))
    thread.start()
    socketVar = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socketVar.bind((IP, UDP_PORT))

    while True:
        data, client_address = socketVar.recvfrom(MESSAGE_SIZE)
        if client_address not in clientsDict:
            clientsDict[client_address] = {
                "bytesReceived": len(data),
                "noMessagesReceived": 1,
                "addDate": datetime.datetime.now()
            }
        else:
            existingClientData = clientsDict[client_address]
            clientsDict[client_address] = {
                "bytesReceived": existingClientData["bytesReceived"] + len(data),
                "noMessagesReceived": existingClientData["noMessagesReceived"] + 1,
                "addDate": datetime.datetime.now()
            }
        socketVar.sendto(str.encode("ACK"), client_address)

def connectionUdpHandler(clientsDict):
    while True:
        removeClients = []
        for address, client in clientsDict.items():
            clientDate = client["addDate"] + datetime.timedelta(0,1)
            if clientDate < datetime.datetime.now():
                print("Protocol: UDP")
                print("Bytes Received : " + str(client["bytesReceived"]))
                print("Messages Received : " + str(client["noMessagesReceived"]))
                removeClients.append(address)
        for client in removeClients:
            clientsDict.pop(client)

if __name__ == '__main__':
    print('Choose protocol: tcp/udp')
    protocol = input()
    if protocol == "tcp":
        connectTcp()
    elif protocol == "udp":
        connectUdp()