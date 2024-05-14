import socket
import time

def udp_receive():
        
    NEW_FILE_PATH = "UDP/new_orders.xml"

    UDP_IP = "127.0.0.1"  # Loopback address 
    UDP_PORT = 24680
    BUFFER_SIZE = 4096
    TIMEOUT = 5  # Timeout in seconds

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    #sock.settimeout(TIMEOUT)  # Set timeout for recvfrom

    try:
        received_data = b""
        while True:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            received_data += data

            # Check for termination message (modify if needed)
            if b"<END_OF_FILE>" in data:
                break
    except socket.timeout:
        print("Timeout occurred, no data received within", TIMEOUT, "seconds.")
    else:
        with open(NEW_FILE_PATH, "wb") as f:
            f.write(received_data[:-len(b"<END_OF_FILE>")])
        print(f"File received and saved at {NEW_FILE_PATH}")

    finally:
        sock.close()

    return NEW_FILE_PATH

if __name__ == "__main__":
    udp_receive()