import socket
import sys
import time

HOST = '127.0.0.1'
PORT = 65431

MESSAGE_SIZE_MAX = 10000
TOTAL_SIZE = 100

mechanism = "streaming" if len(sys.argv) < 3 else sys.argv[2]
protocol = "tcp" if len(sys.argv) < 2 else sys.argv[1]


def start_client_tcp():
    message_count = 0
    byte_count = 0
    start_time = time.time()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        sock.connect((HOST, PORT))
        with open("data.txt", "rb") as file:
            data = file.read()
            for i in range(0, TOTAL_SIZE):
                chunks = [data[j:j + MESSAGE_SIZE_MAX] for j in range(0, len(data), MESSAGE_SIZE_MAX)]
                for chunk in chunks:
                    acknowledged_flag = False
                    sock.send(str.encode(str(chunk)))
                    byte_count += len(data)
                    message_count += 1
                    if mechanism == 'stop-and-wait':
                        while not acknowledged_flag:
                            try:
                                ack_message_from_server = sock.recv(MESSAGE_SIZE_MAX)
                                acknowledged_flag = True
                            except sock.timeout:
                                sock.send(str.encode(str(chunk)))
                                byte_count += len(data)
                                message_count += 1
        sock.close()
    elapsed_time = time.time() - start_time
    print("Client sent {} messages and {} bytes in {}".format(message_count, byte_count, elapsed_time))


def start_client_udp():
    message_count = 0
    byte_count = 0
    start_time = time.time()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(3)
        with open("data.txt", "rb") as file:
            data = file.read()
            for i in range(0, TOTAL_SIZE):
                chunks = [data[j:j + MESSAGE_SIZE_MAX] for j in range(0, len(data), MESSAGE_SIZE_MAX)]
                for chunk in chunks:
                    acknowledged_flag = False
                    sock.sendto(str.encode(str(chunk)), (HOST, PORT))
                    byte_count += len(data)
                    message_count += 1
                    if mechanism == 'stop-and-wait':
                        while not acknowledged_flag:
                            try:
                                ackMessage, address = sock.recvfrom(MESSAGE_SIZE_MAX)
                                acknowledged_flag = True
                            except socket.timeout:
                                sock.sendto(str.encode(str(chunk)), (HOST, PORT))
                                byte_count += len(data)
                                message_count += 1
    elapsed_time = time.time() - start_time
    print("Client sent {} messages and {} bytes in {}".format(message_count, byte_count, elapsed_time))


if __name__ == '__main__':
    if protocol == "tcp":
        start_client_tcp()
    elif protocol == "udp":
        start_client_udp()
