def udp_receive():
    import socket
    import errno

    new_file_path = "new_orders.xml"

    # Host and port to listen on
    HOST = '127.0.0.1'  # Loopback address for same machine communication
    PORT = 24680
    TIMEOUT = 2

    # Buffer size for receiving data (max payload size for IPv4 UDP packets)
    BUFFER_SIZE = 65507

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Bind the socket to the host and port
    sock.bind((HOST, PORT))

    # Set timeout
    sock.settimeout(TIMEOUT)

    while True:
        try:    
            
            with open(new_file_path, 'wb') as f:
                # Receive data from the client
                data = sock.recv(BUFFER_SIZE)
                f.write(data)

                # If the received data is less than the buffer size, it means we have received the whole file
                if len(data) < BUFFER_SIZE:
                    break

        except KeyboardInterrupt:
            print("Exiting...")
            exit(0)
        except socket.error as e:
            new_file_path = None
            break
    
        finally:
            # Close the socket
            sock.close()
            return new_file_path

if __name__ == "__main__":
    udp_receive()