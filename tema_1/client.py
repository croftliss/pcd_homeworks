import socket
import sys
import time

IP = "127.0.0.1"
UDP_PORT = 5000
TCP_PORT = 5001
MESSAGE_SIZE = 65535
MESSAGE_SIZE_MIN = 1024
startTime = time.time()
messageSize = 10000 if len(sys.argv) < 5 else int(sys.argv[4])
totalSendSize = 100 if len(sys.argv) < 4 else int(sys.argv[3])
mechanism = "streaming" if len(sys.argv) < 3 else sys.argv[2]
protocol = "tcp" if len(sys.argv) < 2 else sys.argv[1]

def handleUdpConnection(data):
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.settimeout(1)

    if mechanism == "streaming":
        (bytesSent, noMessagesSent) = handleStreaming(sock, data)
    elif mechanism == "stop-and-wait":
        (bytesSent, noMessagesSent) = handleStopAndWait(sock, data)        
    sock.close()
    return (bytesSent, noMessagesSent)     

def handleStopAndWait(sock, data):
    bytesSent = 0
    noMessagesSent = 0
    try:
        for i in range(0,totalSendSize):
            chunks = [data[j:j+messageSize] for j in range(0, len(data), messageSize)]
            for chunk in chunks:
                acknowledged = False
                if protocol == "tcp":
                    sock.send(str.encode(str(chunk)))
                elif protocol == "udp":
                    sock.sendto(str.encode(str(chunk)), (IP, UDP_PORT))
                bytesSent += len(chunk)
                noMessagesSent += 1
                while not acknowledged:
                    try:
                        if protocol == "tcp":
                            ackMessage = sock.recv(MESSAGE_SIZE)
                        elif protocol == "udp":
                            ackMessage, address = sock.recvfrom(MESSAGE_SIZE_MIN)
                        acknowledged = True
                    except socket.timeout:
                        if protocol == "tcp":
                            sock.send(str.encode(str(chunk)))
                        elif protocol == "udp":
                            sock.sendto(str.encode(str(chunk)), (IP, UDP_PORT))
                        bytesSent += len(chunk)
                        noMessagesSent += 1
    except:
        print("Problem encountered when handling stop-and-waiting.")            
    return (bytesSent, noMessagesSent)

def handleStreaming(sock, data):
    bytesSent = 0
    noMessagesSent = 0
    try:
        for i in range(0, totalSendSize):
            chunks = [data[j : j + messageSize] for j in range(0, len(data), messageSize)]
            for chunk in chunks:
                if protocol == "tcp":
                    sock.send(str.encode(str(chunk)))
                elif protocol == "udp":
                    sock.sendto(str.encode(str(chunk)), (IP, UDP_PORT))
                bytesSent += len(chunk)
                noMessagesSent += 1
    except:
        print("Problem encountered when handling streaming.")            
    return (bytesSent, noMessagesSent)

def handleTcpConnection(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    sock.connect((IP, TCP_PORT))

    if mechanism == "streaming":
        (bytesSent, noMessagesSent) = handleStreaming(sock, data)
    elif mechanism == "stop-and-wait":
        (bytesSent, noMessagesSent) = handleStopAndWait(sock, data)        
    sock.close()
    return (bytesSent, noMessagesSent)

if __name__ == '__main__':
    with open('data.txt', 'r') as file:
        data = file.read().replace('\n', '')
    if protocol == "tcp":
        (bytesSent, noMessagesSent) = handleTcpConnection(data)
        elapsedTime = time.time() - startTime
        print("Elapsed Time : " + str(elapsedTime))
        print("Bytes Sent : " + str(bytesSent))
        print("Messages Sent : " + str(noMessagesSent))
    elif protocol == "udp":
        (bytesSent, noMessagesSent) = handleUdpConnection(data)
        elapsedTime = time.time() - startTime
        print("Elapsed Time : " + str(elapsedTime))
        print("Bytes Sent : " + str(bytesSent))
        print("Messages Sent : " + str(noMessagesSent))