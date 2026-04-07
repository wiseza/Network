# ________________________________________
# Step 3: Create UDP Sender
# sender.py
import socket
from config import HOST, PORT

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

message = input("Enter message: ")

sock.sendto(message.encode(), (HOST, PORT))
print("[SENDER] Message sent")

sock.close()
