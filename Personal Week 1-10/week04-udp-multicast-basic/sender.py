# Step 2: Multicast Sender
# sender.py
import socket
from config import MULTICAST_GROUP, PORT, TTL

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

message = input("Enter multicast message: ")
sock.sendto(message.encode(), (MULTICAST_GROUP, PORT))

print("[SENDER] Multicast sent")
sock.close()
