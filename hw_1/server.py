import socket
import sys

HOST = '127.0.0.1'
PORT = 65431
MESSAGE_SIZE_MAX = 65535

mechanism = "streaming" if len(sys.argv) < 3 else sys.argv[2]
protocol = "tcp" if len(sys.argv) < 2 else sys.argv[1]


def start_server_tcp():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        message_count = 0
        byte_count = 0
        while True:
            data = conn.recv(MESSAGE_SIZE_MAX)
            if not data:
                break
            # Process the received data here
            byte_count += len(data)
            message_count += 1
            if mechanism == 'stop-and-wait':
                # For stop-and-wait just send and ack message
                conn.send(str.encode("ACK"))
        conn.close()
        print("Server received {} messages and {} bytes".format(message_count, byte_count))


def start_server_udp():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        message_count = 0
        byte_count = 0
        while True:
            data, addr = s.recvfrom(MESSAGE_SIZE_MAX)
            if not data:
                break
            byte_count += len(data)
            message_count += 1
            if mechanism == 'stop-and-wait':
                s.sendto(str.encode('ACK'), (addr[0], addr[1]))
            print(f"Message {message_count}: {byte_count} bytes received...")
        s.close()


if __name__ == '__main__':
    if protocol == "tcp":
        start_server_tcp()
    elif protocol == "udp":
        start_server_udp()
