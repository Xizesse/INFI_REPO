def udp_receive():
    import socket

    new_file_path = "new_orders.xml"

    # Host and port to listen on
    HOST = '127.0.0.1'  # Loopback address for same machine communication
    PORT = 24680

    # Buffer size for receiving data (max payload size for IPv4 UDP packets)
    BUFFER_SIZE = 65507

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the host and port
    sock.bind((HOST, PORT))

    try:
        # Receive data until the buffer size is filled
        with open(new_file_path, 'wb') as f:
            while True:
                # Receive data from the client
                data = sock.recv(BUFFER_SIZE)
                f.write(data)

                # If the received data is less than the buffer size, it means we have received the whole file
                if len(data) < BUFFER_SIZE:
                    break

        print(f"File received and saved as '{new_file_path}'")
        return new_file_path

    finally:
        # Close the socket
        sock.close()

if __name__ == "__main__":
    udp_receive()