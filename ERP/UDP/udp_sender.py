import socket
    
# Specify host IP (loopback address for same machine communication)
HOST = "127.0.0.1"

# Port number (ensure it matches the receiver's port)
PORT = 31337

# Set path to your file (replace with the actual location)
FILE_PATH = "order_files\command2a.xml"

# Open the file in binary mode
try:
    with open(FILE_PATH, "rb") as f:
        file_data = f.read()
except FileNotFoundError:
    print(f"Error: File '{FILE_PATH}' not found.")
    exit()

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send the file data and termination message
try:
    sent = sock.sendto(file_data + b"<END_OF_FILE>", (HOST, PORT))
    print(f"Sent {sent} bytes of data to {HOST}:{PORT}")
except Exception as e:
    print(f"Error sending data: {e}")
finally:
    sock.close()

print("Program terminated.")
